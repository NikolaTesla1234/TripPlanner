from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app import models, schemas, crud, auth
from app.database import engine, get_db, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TripPlanner")

# Абсолютные пути к папкам шаблонов и статики (работает из любой рабочей директории)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 environment (без Jinja2Templates из starlette — проблемы с кэшем globals)
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(name: str, **context) -> HTMLResponse:
    template = env.get_template(name)
    html = template.render(**context)
    return HTMLResponse(content=html)


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
    return render_template("trips.html", user=user, trips=trips)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template("login.html")


@app.post("/login")
def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return render_template("login.html", error="Неверный логин или пароль")
    token = auth.create_access_token({"sub": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render_template("register.html")


@app.post("/register")
def register(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    if len(username) < 3 or len(password) < 3:
        return render_template(
            "register.html", error="Логин и пароль должны быть не менее 3 символов"
        )
    if crud.get_user_by_username(db, username):
        return render_template(
            "register.html", error="Пользователь уже существует"
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
    return render_template("trip_form.html", user=user, trip=None)


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

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return render_template(
            "trip_form.html",
            user=user,
            trip=None,
            error="Некорректный формат даты. Используйте ГГГГ-ММ-ДД",
            form_title=title,
            form_destination=destination,
            form_start_date=start_date,
            form_end_date=end_date,
            form_budget=budget,
            form_description=description,
        )
    if start > end:
        return render_template(
            "trip_form.html",
            user=user,
            trip=None,
            error="Дата начала не может быть позже даты окончания",
            form_title=title,
            form_destination=destination,
            form_start_date=start_date,
            form_end_date=end_date,
            form_budget=budget,
            form_description=description,
        )

    trip = schemas.TripCreate(
        title=title,
        destination=destination,
        start_date=start,
        end_date=end,
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
    return render_template(
        "trip_detail.html", user=user, trip=trip, plan_items=plan_items
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
    return render_template("plan_form.html", user=user, trip=trip)


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
    try:
        parsed_date = d.fromisoformat(date)
    except ValueError:
        return render_template(
            "plan_form.html",
            user=user,
            trip=trip,
            error="Некорректный формат даты. Используйте ГГГГ-ММ-ДД",
            form_title=title,
            form_date=date,
            form_time=time,
            form_description=description,
        )
    item = schemas.PlanItemCreate(
        title=title,
        date=parsed_date,
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
    by_destination = {}
    for t in trips:
        by_destination[t.destination] = by_destination.get(t.destination, 0) + 1
    return render_template(
        "stats.html",
        user=user,
        total_trips=total_trips,
        total_budget=total_budget,
        avg_budget=round(avg_budget, 2),
        by_destination=by_destination.items(),
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
