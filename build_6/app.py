"""
TripPlanner — БИЛД 6 (ИТОГОВЫЙ)
===============================
Веб-интерфейс на Flask. Все 4 сущности:
  • Поездка (Trip)
  • Пункт плана с датой (PlanItem)
  • Бюджет (BudgetItem)
  • План по дням (DayPlan)

Запуск:
    pip install -r requirements.txt
    python app.py
Затем откройте http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import TripPlanner

app = Flask(__name__)
app.secret_key = "trip-planner-secret-key"

planner = TripPlanner()


# ---------- главная: список поездок ----------
@app.route("/")
def index():
    trips = planner.list_trips()
    return render_template("index.html", trips=trips)


# ---------- добавление поездки ----------
@app.route("/trips/add", methods=["GET", "POST"])
def add_trip():
    if request.method == "POST":
        planner.add_trip(
            title=request.form["title"],
            destination=request.form["destination"],
            start_date=request.form["start_date"],
            end_date=request.form["end_date"],
            description=request.form.get("description", ""),
        )
        flash("Поездка добавлена!", "success")
        return redirect(url_for("index"))
    return render_template("trip_form.html", trip=None, action=url_for("add_trip"))


# ---------- удаление поездки ----------
@app.route("/trips/<int:trip_id>/delete")
def delete_trip(trip_id):
    planner.delete_trip(trip_id)
    flash("Поездка удалена.", "info")
    return redirect(url_for("index"))


# ---------- детальная страница поездки ----------
@app.route("/trips/<int:trip_id>")
def trip_detail(trip_id):
    trip = planner.find_trip(trip_id)
    if not trip:
        flash("Поездка не найдена.", "danger")
        return redirect(url_for("index"))
    plan_items = planner.list_plan_items(trip_id)
    budget_items = planner.list_budget_items(trip_id)
    day_plans = planner.list_day_plans(trip_id)
    planned, actual = planner.trip_budget_summary(trip_id)
    return render_template(
        "trip.html",
        trip=trip,
        plan_items=plan_items,
        budget_items=budget_items,
        day_plans=day_plans,
        planned=planned,
        actual=actual,
    )


# ---------- пункт плана ----------
@app.route("/trips/<int:trip_id>/plan/add", methods=["POST"])
def add_plan_item(trip_id):
    planner.add_plan_item(
        trip_id=trip_id,
        title=request.form["title"],
        date=request.form["date"],
        time=request.form.get("time", ""),
        description=request.form.get("description", ""),
    )
    flash("Пункт плана добавлен.", "success")
    return redirect(url_for("trip_detail", trip_id=trip_id))


@app.route("/plan/<int:item_id>/delete")
def delete_plan_item(item_id):
    # найдём trip_id до удаления
    trip_id = None
    for i in planner.plan_items:
        if i.id == item_id:
            trip_id = i.trip_id
            break
    planner.delete_plan_item(item_id)
    flash("Пункт плана удалён.", "info")
    return redirect(url_for("trip_detail", trip_id=trip_id) if trip_id else url_for("index"))


# ---------- бюджет ----------
@app.route("/trips/<int:trip_id>/budget/add", methods=["POST"])
def add_budget_item(trip_id):
    planner.add_budget_item(
        trip_id=trip_id,
        category=request.form["category"],
        planned=request.form["planned"],
        actual=request.form.get("actual", 0) or 0,
        currency=request.form.get("currency", "руб."),
    )
    flash("Статья бюджета добавлена.", "success")
    return redirect(url_for("trip_detail", trip_id=trip_id))


@app.route("/budget/<int:item_id>/delete")
def delete_budget_item(item_id):
    trip_id = None
    for b in planner.budget_items:
        if b.id == item_id:
            trip_id = b.trip_id
            break
    planner.delete_budget_item(item_id)
    flash("Статья бюджета удалена.", "info")
    return redirect(url_for("trip_detail", trip_id=trip_id) if trip_id else url_for("index"))


# ---------- план по дням ----------
@app.route("/trips/<int:trip_id>/day/add", methods=["POST"])
def add_day_plan(trip_id):
    acts_raw = request.form.get("activities", "")
    activities = [a.strip() for a in acts_raw.split(",") if a.strip()]
    planner.add_day_plan(
        trip_id=trip_id,
        day_number=request.form["day_number"],
        date=request.form["date"],
        activities=activities,
        notes=request.form.get("notes", ""),
    )
    flash("День добавлен в план.", "success")
    return redirect(url_for("trip_detail", trip_id=trip_id))


@app.route("/day/<int:item_id>/delete")
def delete_day_plan(item_id):
    trip_id = None
    for d in planner.day_plans:
        if d.id == item_id:
            trip_id = d.trip_id
            break
    planner.delete_day_plan(item_id)
    flash("День удалён из плана.", "info")
    return redirect(url_for("trip_detail", trip_id=trip_id) if trip_id else url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
