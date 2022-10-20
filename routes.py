import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app
import uuid
# from collections import defaultdict

pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")
# completions = defaultdict(list)


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day) #by default , time, min, sec are 0


@pages.route("/")
def index():
    # print([e for e in app.db.habits.find({})])
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    # habits= [
    #     (habit['habit'])
    #     for habit in current_app.db.habits.find({})
    # ]

    habits_on_current_date = current_app.db.habits.find(
        {"added_date": {"$lte": selected_date}}
    )

    completions = [
        habit['habit']
        for habit in current_app.db.completions.find({"date": selected_date})
    ]
    return render_template(
        "index.html",
        title="Habit Tracker - Home",
        habits=habits_on_current_date,
        completions=completions,
        selected_date=selected_date
    )


@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get('date')
    date = datetime.datetime.fromisoformat(date_string)
    habitId = request.form.get('habitId')
    # completions[date].append(habit)
    current_app.db.completions.insert_one({
        "date": date, "habit": habitId
    })
    return redirect(url_for("habits.index", date=date_string))


@pages.route("/add/", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.method == "POST":
        habit = request.form.get('habit')
        current_app.db.habits.insert_one({"_id": uuid.uuid4().hex, "added_date": today, "habit": habit})

    return render_template(
            "add_habit.html",
            title="Habit Tracker - Add Habit",
            selected_date=today
        )
