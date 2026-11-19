"""
TripPlanner — БИЛД 4
====================
Что сделано: Поездка + Пункт плана + Бюджет + План по дням (DayPlan).
Можно: составить по дням, что именно будет происходить в поездке.

Запуск: python main.py
"""


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

    def __str__(self):
        total_planned = sum(b.planned for b in self.budget_items)
        total_actual = sum(b.actual for b in self.budget_items)
        return (f"[{self.id}] {self.title}\n"
                f"   Куда: {self.destination}\n"
                f"   Когда: {self.start_date} — {self.end_date}\n"
                f"   Бюджет: запл. {total_planned}, факт. {total_actual}\n"
                f"   Дней в плане: {len(self.day_plans)}")

    def add_plan_item(self, item):
        self.plan_items.append(item)

    def add_budget_item(self, item):
        self.budget_items.append(item)

    def add_day_plan(self, item):
        self.day_plans.append(item)

    def get_plan_items(self):
        return sorted(self.plan_items, key=lambda x: x.date)

    def get_budget_items(self):
        return self.budget_items

    def get_day_plans(self):
        return sorted(self.day_plans, key=lambda x: x.day_number)


class PlanItem:
    def __init__(self, id, trip_id, title, date, time, description=""):
        self.id = id
        self.trip_id = trip_id
        self.title = title
        self.date = date
        self.time = time
        self.description = description

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

    def __str__(self):
        return (f"   [{self.id}] {self.category}: запл. {self.planned} {self.currency}, "
                f"факт. {self.actual} {self.currency}")


class DayPlan:
    """План на один день поездки."""
    def __init__(self, id, trip_id, day_number, date, activities, notes=""):
        self.id = id
        self.trip_id = trip_id
        self.day_number = day_number   # 1, 2, 3...
        self.date = date               # "ГГГГ-ММ-ДД"
        self.activities = activities   # список строк — чем занимаемся
        self.notes = notes

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

    def add_trip(self, title, destination, start_date, end_date, description=""):
        trip = Trip(self.next_trip_id, title, destination, start_date, end_date, description)
        self.trips.append(trip)
        self.next_trip_id += 1
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

    # --- пункты плана ---
    def add_plan_item(self, trip_id, title, date, time, description=""):
        item = PlanItem(self.next_item_id, trip_id, title, date, time, description)
        self.plan_items.append(item)
        trip = self.find_trip(trip_id)
        if trip:
            trip.add_plan_item(item)
        self.next_item_id += 1
        return item

    def list_plan_items(self, trip_id):
        trip = self.find_trip(trip_id)
        return trip.get_plan_items() if trip else []

    def delete_plan_item(self, item_id):
        self.plan_items = [i for i in self.plan_items if i.id != item_id]
        for t in self.trips:
            t.plan_items = [i for i in t.plan_items if i.id != item_id]

    # --- бюджет ---
    def add_budget_item(self, trip_id, category, planned, actual=0, currency="руб."):
        item = BudgetItem(self.next_budget_id, trip_id, category, planned, actual, currency)
        self.budget_items.append(item)
        trip = self.find_trip(trip_id)
        if trip:
            trip.add_budget_item(item)
        self.next_budget_id += 1
        return item

    def list_budget_items(self, trip_id):
        trip = self.find_trip(trip_id)
        return trip.get_budget_items() if trip else []

    def delete_budget_item(self, item_id):
        self.budget_items = [b for b in self.budget_items if b.id != item_id]
        for t in self.trips:
            t.budget_items = [b for b in t.budget_items if b.id != item_id]

    # --- план по дням ---
    def add_day_plan(self, trip_id, day_number, date, activities, notes=""):
        item = DayPlan(self.next_day_id, trip_id, day_number, date, activities, notes)
        self.day_plans.append(item)
        trip = self.find_trip(trip_id)
        if trip:
            trip.add_day_plan(item)
        self.next_day_id += 1
        return item

    def list_day_plans(self, trip_id):
        trip = self.find_trip(trip_id)
        return trip.get_day_plans() if trip else []

    def delete_day_plan(self, item_id):
        self.day_plans = [d for d in self.day_plans if d.id != item_id]
        for t in self.trips:
            t.day_plans = [d for d in t.day_plans if d.id != item_id]

    def trip_budget_summary(self, trip_id):
        items = self.list_budget_items(trip_id)
        planned = sum(b.planned for b in items)
        actual = sum(b.actual for b in items)
        return planned, actual


def print_menu():
    print("\n=== ПЛАНИРОВЩИК ПОЕЗДОК (БИЛД 4) ===")
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

    planner.add_trip("Поездка в Москву", "Москва", "2024-06-01", "2024-06-05", "Туристическая поездка")
    planner.add_trip("Отпуск в Сочи", "Сочи", "2024-07-10", "2024-07-20", "Море и солнце")

    planner.add_plan_item(1, "Поездка на поезде", "2024-06-01", "08:00", "Выезд с вокзала")
    planner.add_plan_item(1, "Экскурсия по Красной площади", "2024-06-02", "10:00", "Групповая экскурсия")

    planner.add_budget_item(1, "Транспорт", 5000, 4800)
    planner.add_budget_item(1, "Питание", 3000, 3200)
    planner.add_budget_item(1, "Жильё", 8000, 8000)

    planner.add_day_plan(1, 1, "2024-06-01", ["Посадка на поезд", "Приезд в Москву"], "Первый день")
    planner.add_day_plan(1, 2, "2024-06-02", ["Завтрак", "Экскурсия", "Ужин"], "")

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
            print("Поездка добавлена!")

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
            print("До свидания!")
            break

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
