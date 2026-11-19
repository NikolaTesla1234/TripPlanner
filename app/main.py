from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from app import models, schemas, crud, auth
from app.database import engine, get_db, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TripPlanner")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------- Helpers ----------
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    username = auth.decode_token(token)
    if not username:
        return None
    return crud.get_user_by_username(db, username)


def require_user(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=302, headers={"location": "/login"})
    return user


# ---------- Pages ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    trips = crud.get_trips_by_owner(db, user.id)
    return templates.TemplateResponse("trips.html", {"request": request, "user": user, "trips": trips})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Неверный логин или пароль"}
        )
    token = auth.create_access_token({"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    if len(username) < 3 or len(password) < 3:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Логин и пароль должны быть не менее 3 символов"}
        )
    if crud.get_user_by_username(db, username):
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Пользователь уже существует"}
        )
    crud.create_user(db, schemas.UserCreate(username=username, password=password))
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response


@app.get("/trips/new", response_class=HTMLResponse)
def new_trip_page(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse("trip_form.html", {"request": request, "user": user, "trip": None})


@app.post("/trips/new")
def create_trip(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    title: str = Form(...),
    destination: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    budget: float = Form(0.0),
    description: str = Form(""),
):
    from datetime import date

    trip = schemas.TripCreate(
        title=title,
        destination=destination,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        budget=budget,
        description=description,
    )
    crud.create_trip(db, trip, user.id)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.get("/trips/{trip_id}", response_class=HTMLResponse)
def trip_detail(request: Request, trip_id: int, db: Session = Depends(get_db), user=Depends(require_user)):
    trip = crud.get_trip(db, trip_id)
    if not trip or trip.owner_id != user.id:
        raise HTTPException(status_code=404)
    plan_items = crud.get_plan_items_by_trip(db, trip_id)
    return templates.TemplateResponse(
        "trip_detail.html", {"request": request, "user": user, "trip": trip, "plan_items": plan_items}
    )


@app.post("/trips/{trip_id}/delete")
def delete_trip(trip_id: int, db: Session = Depends(get_db), user=Depends(require_user)):
    ok = crud.delete_trip(db, trip_id, user.id)
    if not ok:
        raise HTTPException(status_code=404)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@app.post("/trips/{trip_id}/like")
def like_trip(trip_id: int, db: Session = Depends(get_db), user=Depends(require_user)):
    ok = crud.like_trip(db, trip_id)
    if not ok:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=f"/trips/{trip_id}", status_code=status.HTTP_302_FOUND)


@app.get("/trips/{trip_id}/plan/new", response_class=HTMLResponse)
def new_plan_item_page(request: Request, trip_id: int, db: Session = Depends(get_db), user=Depends(require_user)):
    trip = crud.get_trip(db, trip_id)
    if not trip or trip.owner_id != user.id:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("plan_form.html", {"request": request, "user": user, "trip": trip})


@app.post("/trips/{trip_id}/plan/new")
def create_plan_item(
    request: Request,
    trip_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_user),
    title: str = Form(...),
    date: str = Form(...),
    time: str = Form(""),
    description: str = Form(""),
):
    from datetime import date as d

    trip = crud.get_trip(db, trip_id)
    if not trip or trip.owner_id != user.id:
        raise HTTPException(status_code=404)
    item = schemas.PlanItemCreate(
        title=title,
        date=d.fromisoformat(date),
        time=time,
        description=description,
    )
    crud.create_plan_item(db, item, trip_id)
    return RedirectResponse(url=f"/trips/{trip_id}", status_code=status.HTTP_302_FOUND)


@app.get("/stats", response_class=HTMLResponse)
def stats_page(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    trips = crud.get_trips_by_owner(db, user.id)
    total_trips = len(trips)
    total_budget = sum(t.budget for t in trips)
    avg_budget = total_budget / total_trips if total_trips else 0
    # grouping by destination
    by_destination = {}
    for t in trips:
        by_destination[t.destination] = by_destination.get(t.destination, 0) + 1
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "user": user,
            "total_trips": total_trips,
            "total_budget": total_budget,
            "avg_budget": round(avg_budget, 2),
            "by_destination": by_destination.items(),
        },
    )


# ---------- API ----------
@app.get("/api/users/", response_model=list[schemas.UserOut])
def api_users(db: Session = Depends(get_db), user=Depends(require_user)):
    return crud.get_users(db)


@app.post("/api/trips/", response_model=schemas.TripOut)
def api_create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    return crud.create_trip(db, trip, user.id)


@app.get("/api/trips/", response_model=list[schemas.TripOut])
def api_list_trips(db: Session = Depends(get_db), user=Depends(require_user)):
    return crud.get_trips_by_owner(db, user.id)
