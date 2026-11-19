"""
TripPlanner — БИЛД 1
====================
Что сделано: базовая модель Поездка (Trip) и консольный интерфейс.
Можно: добавлять, смотреть и удалять поездки.

Запуск: python main.py
"""

from datetime import date


class Trip:
    """Одна поездка."""
    def __init__(self, id, title, destination, start_date, end_date, description=""):
        self.id = id
        self.title = title
        self.destination = destination
        self.start_date = start_date   # строка "ГГГГ-ММ-ДД"
        self.end_date = end_date       # строка "ГГГГ-ММ-ДД"
        self.description = description

    def __str__(self):
        return (f"[{self.id}] {self.title}\n"
                f"   Куда: {self.destination}\n"
                f"   Когда: {self.start_date} — {self.end_date}\n"
                f"   Описание: {self.description}")


class TripPlanner:
    """Менеджер поездок (в памяти)."""
    def __init__(self):
        self.trips = []
        self.next_id = 1

    def add_trip(self, title, destination, start_date, end_date, description=""):
        trip = Trip(self.next_id, title, destination, start_date, end_date, description)
        self.trips.append(trip)
        self.next_id += 1
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


def print_menu():
    print("\n=== ПЛАНИРОВЩИК ПОЕЗДОК (БИЛД 1) ===")
    print("1. Показать все поездки")
    print("2. Добавить поездку")
    print("3. Удалить поездку")
    print("0. Выход")


def main():
    planner = TripPlanner()

    # демо-данные, чтобы сразу было что показывать
    planner.add_trip("Поездка в Москву", "Москва", "2024-06-01", "2024-06-05", "Туристическая поездка")
    planner.add_trip("Отпуск в Сочи", "Сочи", "2024-07-10", "2024-07-20", "Море и солнце")

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
                print("Поездка удалена.")
            else:
                print("Поездка с таким ID не найдена.")

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор, попробуйте ещё раз.")


if __name__ == "__main__":
    main()
