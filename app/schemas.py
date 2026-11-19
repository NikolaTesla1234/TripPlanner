from pydantic import BaseModel
from datetime import date


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TripBase(BaseModel):
    title: str
    destination: str
    start_date: date
    end_date: date
    budget: float = 0.0
    description: str = ""


class TripCreate(TripBase):
    pass


class TripOut(TripBase):
    id: int
    owner_id: int
    likes: int

    class Config:
        from_attributes = True


class PlanItemBase(BaseModel):
    title: str
    date: date
    time: str = ""
    description: str = ""


class PlanItemCreate(PlanItemBase):
    pass


class PlanItemOut(PlanItemBase):
    id: int
    trip_id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str
