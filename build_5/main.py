"""
TripPlanner — БИЛД 5
====================
Что сделано: Поездка + Пункт плана + Бюджет + План по дням + СОХРАНЕНИЕ в JSON.
Данные теперь хранятся в файле data.json и не пропадают после закрытия программы.

Запуск: python main.py
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

    def __str__(self):
        total_planned = sum(b.planned for b in self.budget_items)
        total_actual = sum(b.actual for b in self.budget_items)
        return (f"[{self.id}] {self.title}\n"
                f"   Куда: {self.destination}\n"
                f"   Когда: {self.start_date} — {self.end_date}\n"
                f"   Бюджет: запл. {total_planned}, факт. {total_actual}\n"
                f"   Дней в плане: {len(self.day_plans)}")


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

    def __str__(self):
        return f"   [{self.id}] {self.title} — {self.date} {self.time}\n       {self.description}"


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

    def __str__(self):
        return (f"   [{self.id}] {self.category}: запл. {self.planned} {self.currency}, "
                f"факт. {self.actual} {self.currency}")


class DayPlan:
    def __init__(self, id, trip_id, day_number, date, activities, notes=""):
        self.id = id
        self.trip_id = trip_id
        self.day_number = day_number
        self.date = date
        self.activities = activities
        self.notes = notes

    def to_dict(self):
        return {"id": self.id, "trip_id": self.trip_id, "day_number": self.day_number,
                "date": self.date, "activities": self.activities, "notes": self.notes}

    def __str__(self):
        acts = "\n         • ".join(self.activities) if self.activities else "(нет мероприятий)"
        return (f"   [{self.id}] День {self.day_number} ({self.date})\n"
                f"         • {acts}\n"
                f"         Заметки: {self.notes}")


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

    # ---------- загрузка / сохранение ----------
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
        # восстановим связи объектов
        for t in self.trips:
            t.plan_items = [i for i in self.plan_items if i.trip_id == t.id]
            t.budget_items = [b for b in self.budget_items if b.trip_id == t.id]
            t.day_plans = [d for d in self.day_plans if d.trip_id == t.id]

    # ---------- поездки ----------
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

    # ---------- пункты плана ----------
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

    # ---------- бюджет ----------
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
        planned = sum(b.planned for b in items)
        actual = sum(b.actual for b in items)
        return planned, actual

    # ---------- план по дням ----------
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


def print_menu():
    print("\n=== ПЛАНИРОВЩИК ПОЕЗДОК (БИЛД 5) ===")
    print("1. Показать все поездки")
    print("2. Добавить поездку")
    print("3. Удалить поездку")
    print("4. План поездки (пункты с датами)")
    print("5. Добавить пункт плана")
    print("6. Удалить пункт плана")
    print("7. Бюджет поездки")
    print("8. Добавить статью бюджета")
    print("9. Удалить статью бюджета")
    print("10. План по дням поездки")
    print("11. Добавить день в план")
    print("12. Удалить день из плана")
    print("0. Выход")


def main():
    planner = TripPlanner()
    planner.load()  # загружаем данные из файла при запуске

    # если данных нет — добавим демо
    if not planner.list_trips():
        planner.add_trip("Поездка в Москву", "Москва", "2024-06-01", "2024-06-05", "Туристическая поездка")
        planner.add_trip("Отпуск в Сочи", "Сочи", "2024-07-10", "2024-07-20", "Море и солнце")
        planner.add_plan_item(1, "Поездка на поезде", "2024-06-01", "08:00", "Выезд с вокзала")
        planner.add_plan_item(1, "Экскурсия по Красной площади", "2024-06-02", "10:00", "Экскурсия")
        planner.add_budget_item(1, "Транспорт", 5000, 4800)
        planner.add_budget_item(1, "Питание", 3000, 3200)
        planner.add_budget_item(1, "Жильё", 8000, 8000)
        planner.add_day_plan(1, 1, "2024-06-01", ["Посадка на поезд", "Приезд в Москву"], "Первый день")
        planner.add_day_plan(1, 2, "2024-06-02", ["Завтрак", "Экскурсия", "Ужин"], "")
        planner.save()

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            for t in planner.list_trips():
                print(t)
                print("-" * 30)

        elif choice == "2":
            title = input("Название поездки: ")
            destination = input("Пункт назначения: ")
            start_date = input("Дата начала (ГГГГ-ММ-ДД): ")
            end_date = input("Дата конца (ГГГГ-ММ-ДД): ")
            description = input("Описание: ")
            planner.add_trip(title, destination, start_date, end_date, description)
            print("Поездка добавлена и сохранена!")

        elif choice == "3":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            if planner.find_trip(trip_id):
                planner.delete_trip(trip_id)
                print("Поездка удалена.")
            else:
                print("Не найдено.")

        elif choice == "4":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            for it in planner.list_plan_items(trip_id):
                print(it)
                print("-" * 30)

        elif choice == "5":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            if not planner.find_trip(trip_id):
                print("Поездка не найдена.")
                continue
            title = input("Название пункта: ")
            date = input("Дата (ГГГГ-ММ-ДД): ")
            time = input("Время (ЧЧ:ММ): ")
            desc = input("Описание: ")
            planner.add_plan_item(trip_id, title, date, time, desc)
            print("Добавлено!")

        elif choice == "6":
            try:
                item_id = int(input("ID пункта плана: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            planner.delete_plan_item(item_id)
            print("Удалено.")

        elif choice == "7":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            items = planner.list_budget_items(trip_id)
            if not items:
                print("Статьи бюджета не найдены.")
            else:
                print(f"\n--- Бюджет поездки #{trip_id} ---")
                for b in items:
                    print(b)
                planned, actual = planner.trip_budget_summary(trip_id)
                print(f"Итого: запл. {planned}, факт. {actual}")
                print("-" * 30)

        elif choice == "8":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            if not planner.find_trip(trip_id):
                print("Поездка не найдена.")
                continue
            category = input("Категория: ")
            planned = input("Запланировано: ")
            actual = input("Потрачено (0): ") or "0"
            currency = input("Валюта (руб.): ") or "руб."
            planner.add_budget_item(trip_id, category, planned, actual, currency)
            print("Добавлено!")

        elif choice == "9":
            try:
                item_id = int(input("ID статьи бюджета: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            planner.delete_budget_item(item_id)
            print("Удалено.")

        elif choice == "10":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            for d in planner.list_day_plans(trip_id):
                print(d)
                print("-" * 30)

        elif choice == "11":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            if not planner.find_trip(trip_id):
                print("Поездка не найдена.")
                continue
            day_number = input("Номер дня (1, 2...): ")
            date = input("Дата (ГГГГ-ММ-ДД): ")
            acts_raw = input("Мероприятия через запятую: ")
            activities = [a.strip() for a in acts_raw.split(",") if a.strip()]
            notes = input("Заметки: ")
            planner.add_day_plan(trip_id, day_number, date, activities, notes)
            print("День добавлен!")

        elif choice == "12":
            try:
                item_id = int(input("ID дня: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            planner.delete_day_plan(item_id)
            print("Удалено.")

        elif choice == "0":
            print("До свидания! Данные сохранены в data.json")
            break

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
