"""
Модели данных TripPlanner (используются веб-приложением build_6).
Тот же набор сущностей: Поездка, Пункт плана, Бюджет, План по дням.
"""

import json
import os


DATA_FILE = "data.json"


class Trip:
    def __init__(self, id, title, destination, start_date, end_date, description=""):
        self.id = id
        self.title = title
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.plan_items = []
        self.budget_items = []
        self.day_plans = []

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "destination": self.destination,
            "start_date": self.start_date, "end_date": self.end_date,
            "description": self.description,
        }


class PlanItem:
    def __init__(self, id, trip_id, title, date, time, description=""):
        self.id = id
        self.trip_id = trip_id
        self.title = title
        self.date = date
        self.time = time
        self.description = description

    def to_dict(self):
        return {"id": self.id, "trip_id": self.trip_id, "title": self.title,
                "date": self.date, "time": self.time, "description": self.description}


class BudgetItem:
    def __init__(self, id, trip_id, category, planned, actual=0, currency="руб."):
        self.id = id
        self.trip_id = trip_id
        self.category = category
        self.planned = float(planned)
        self.actual = float(actual)
        self.currency = currency

    def to_dict(self):
        return {"id": self.id, "trip_id": self.trip_id, "category": self.category,
                "planned": self.planned, "actual": self.actual, "currency": self.currency}


class DayPlan:
    def __init__(self, id, trip_id, day_number, date, activities, notes=""):
        self.id = id
        self.trip_id = trip_id
        self.day_number = int(day_number)
        self.date = date
        self.activities = list(activities)
        self.notes = notes

    def to_dict(self):
        return {"id": self.id, "trip_id": self.trip_id, "day_number": self.day_number,
                "date": self.date, "activities": self.activities, "notes": self.notes}


class TripPlanner:
    def __init__(self):
        self.trips = []
        self.plan_items = []
        self.budget_items = []
        self.day_plans = []
        self.next_trip_id = 1
        self.next_item_id = 1
        self.next_budget_id = 1
        self.next_day_id = 1
        self.load()

    def save(self):
        data = {
            "next_trip_id": self.next_trip_id,
            "next_item_id": self.next_item_id,
            "next_budget_id": self.next_budget_id,
            "next_day_id": self.next_day_id,
            "trips": [t.to_dict() for t in self.trips],
            "plan_items": [i.to_dict() for i in self.plan_items],
            "budget_items": [b.to_dict() for b in self.budget_items],
            "day_plans": [d.to_dict() for d in self.day_plans],
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.next_trip_id = data.get("next_trip_id", 1)
        self.next_item_id = data.get("next_item_id", 1)
        self.next_budget_id = data.get("next_budget_id", 1)
        self.next_day_id = data.get("next_day_id", 1)
        self.trips = [Trip(**t) for t in data.get("trips", [])]
        self.plan_items = [PlanItem(**i) for i in data.get("plan_items", [])]
        self.budget_items = [BudgetItem(**b) for b in data.get("budget_items", [])]
        self.day_plans = [DayPlan(**d) for d in data.get("day_plans", [])]

    def _links(self):
        for t in self.trips:
            t.plan_items = [i for i in self.plan_items if i.trip_id == t.id]
            t.budget_items = [b for b in self.budget_items if b.trip_id == t.id]
            t.day_plans = [d for d in self.day_plans if d.trip_id == t.id]

    # ----- trips -----
    def add_trip(self, title, destination, start_date, end_date, description=""):
        trip = Trip(self.next_trip_id, title, destination, start_date, end_date, description)
        self.trips.append(trip)
        self.next_trip_id += 1
        self.save()
        return trip

    def list_trips(self):
        return self.trips

    def find_trip(self, trip_id):
        for t in self.trips:
            if t.id == trip_id:
                return t
        return None

    def delete_trip(self, trip_id):
        self.trips = [t for t in self.trips if t.id != trip_id]
        self.plan_items = [i for i in self.plan_items if i.trip_id != trip_id]
        self.budget_items = [b for b in self.budget_items if b.trip_id != trip_id]
        self.day_plans = [d for d in self.day_plans if d.trip_id != trip_id]
        self.save()

    # ----- plan items -----
    def add_plan_item(self, trip_id, title, date, time, description=""):
        item = PlanItem(self.next_item_id, trip_id, title, date, time, description)
        self.plan_items.append(item)
        self.next_item_id += 1
        self.save()
        return item

    def list_plan_items(self, trip_id):
        return sorted([i for i in self.plan_items if i.trip_id == trip_id], key=lambda x: x.date)

    def delete_plan_item(self, item_id):
        self.plan_items = [i for i in self.plan_items if i.id != item_id]
        self.save()

    # ----- budget -----
    def add_budget_item(self, trip_id, category, planned, actual=0, currency="руб."):
        item = BudgetItem(self.next_budget_id, trip_id, category, planned, actual, currency)
        self.budget_items.append(item)
        self.next_budget_id += 1
        self.save()
        return item

    def list_budget_items(self, trip_id):
        return [b for b in self.budget_items if b.trip_id == trip_id]

    def delete_budget_item(self, item_id):
        self.budget_items = [b for b in self.budget_items if b.id != item_id]
        self.save()

    def trip_budget_summary(self, trip_id):
        items = self.list_budget_items(trip_id)
        return sum(b.planned for b in items), sum(b.actual for b in items)

    # ----- day plans -----
    def add_day_plan(self, trip_id, day_number, date, activities, notes=""):
        item = DayPlan(self.next_day_id, trip_id, day_number, date, activities, notes)
        self.day_plans.append(item)
        self.next_day_id += 1
        self.save()
        return item

    def list_day_plans(self, trip_id):
        return sorted([d for d in self.day_plans if d.trip_id == trip_id], key=lambda x: x.day_number)

    def delete_day_plan(self, item_id):
        self.day_plans = [d for d in self.day_plans if d.id != item_id]
        self.save()
