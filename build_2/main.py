"""
TripPlanner — БИЛД 2
====================
Что сделано: Поездка (Trip) + Пункт плана (PlanItem) с датами.
Можно: управлять поездками и привязывать к каждой поездке пункты плана с датой.

Запуск: python main.py
"""

from datetime import date


class Trip:
    """Одна поездка."""
    def __init__(self, id, title, destination, start_date, end_date, description=""):
        self.id = id
        self.title = title
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.plan_items = []  # список пунктов плана этой поездки

    def __str__(self):
        return (f"[{self.id}] {self.title}\n"
                f"   Куда: {self.destination}\n"
                f"   Когда: {self.start_date} — {self.end_date}\n"
                f"   Описание: {self.description}\n"
                f"   Пунктов плана: {len(self.plan_items)}")

    def add_plan_item(self, item):
        self.plan_items.append(item)

    def get_plan_items(self):
        return sorted(self.plan_items, key=lambda x: x.date)


class PlanItem:
    """Пункт плана поездки с датой."""
    def __init__(self, id, trip_id, title, date, time, description=""):
        self.id = id
        self.trip_id = trip_id
        self.title = title
        self.date = date         # дата мероприятия "ГГГГ-ММ-ДД"
        self.time = time         # время "ЧЧ:ММ"
        self.description = description

    def __str__(self):
        return (f"   [{self.id}] {self.title} — {self.date} {self.time}\n"
                f"       {self.description}")


class TripPlanner:
    def __init__(self):
        self.trips = []
        self.plan_items = []
        self.next_trip_id = 1
        self.next_item_id = 1

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
        if not trip:
            return []
        return trip.get_plan_items()

    def delete_plan_item(self, item_id):
        self.plan_items = [i for i in self.plan_items if i.id != item_id]
        for t in self.trips:
            t.plan_items = [i for i in t.plan_items if i.id != item_id]


def print_menu():
    print("\n=== ПЛАНИРОВЩИК ПОЕЗДОК (БИЛД 2) ===")
    print("1. Показать все поездки")
    print("2. Добавить поездку")
    print("3. Удалить поездку")
    print("4. Показать план поездки (пункты с датами)")
    print("5. Добавить пункт плана к поездке")
    print("6. Удалить пункт плана")
    print("0. Выход")


def main():
    planner = TripPlanner()

    planner.add_trip("Поездка в Москву", "Москва", "2024-06-01", "2024-06-05", "Туристическая поездка")
    planner.add_trip("Отпуск в Сочи", "Сочи", "2024-07-10", "2024-07-20", "Море и солнце")

    planner.add_plan_item(1, "Поездка на поезде", "2024-06-01", "08:00", "Выезд с московского вокзала")
    planner.add_plan_item(1, "Экскурсия по Красной площади", "2024-06-02", "10:00", "Групповая экскурсия")
    planner.add_plan_item(2, "Вылет в Сочи", "2024-07-10", "14:00", "Авиарейс")

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            trips = planner.list_trips()
            if not trips:
                print("Поездок пока нет.")
            else:
                print("\n--- Все поездки ---")
                for t in trips:
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
                trip_id = int(input("ID поездки для удаления: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            if planner.find_trip(trip_id):
                planner.delete_trip(trip_id)
                print("Поездка и её план удалены.")
            else:
                print("Поездка не найдена.")

        elif choice == "4":
            try:
                trip_id = int(input("ID поездки: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            items = planner.list_plan_items(trip_id)
            if not items:
                print("Пункты плана не найдены.")
            else:
                print(f"\n--- План поездки #{trip_id} ---")
                for it in items:
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
            title = input("Название пункта плана: ")
            date = input("Дата (ГГГГ-ММ-ДД): ")
            time = input("Время (ЧЧ:ММ): ")
            description = input("Описание: ")
            planner.add_plan_item(trip_id, title, date, time, description)
            print("Пункт плана добавлен!")

        elif choice == "6":
            try:
                item_id = int(input("ID пункта плана для удаления: "))
            except ValueError:
                print("Некорректный ID.")
                continue
            planner.delete_plan_item(item_id)
            print("Пункт плана удалён.")

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
