from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_trip(db: Session, trip_id: int):
    return db.query(models.Trip).filter(models.Trip.id == trip_id).first()


def get_trips_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 20):
    return (
        db.query(models.Trip)
        .filter(models.Trip.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_trip(db: Session, trip: schemas.TripCreate, owner_id: int):
    db_trip = models.Trip(**trip.model_dump(), owner_id=owner_id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def update_trip(db: Session, trip_id: int, trip: schemas.TripCreate, owner_id: int):
    db_trip = get_trip(db, trip_id)
    if not db_trip or db_trip.owner_id != owner_id:
        return None
    for field, value in trip.model_dump().items():
        setattr(db_trip, field, value)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def delete_trip(db: Session, trip_id: int, owner_id: int):
    db_trip = get_trip(db, trip_id)
    if not db_trip or db_trip.owner_id != owner_id:
        return False
    db.delete(db_trip)
    db.commit()
    return True


def like_trip(db: Session, trip_id: int):
    db_trip = get_trip(db, trip_id)
    if not db_trip:
        return False
    db_trip.likes += 1
    db.commit()
    return True


def get_plan_items_by_trip(db: Session, trip_id: int):
    return db.query(models.PlanItem).filter(models.PlanItem.trip_id == trip_id).all()


def create_plan_item(db: Session, item: schemas.PlanItemCreate, trip_id: int):
    db_item = models.PlanItem(**item.model_dump(), trip_id=trip_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
