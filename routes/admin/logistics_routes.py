import uuid
from itertools import groupby

import dateutil.parser
import sqlalchemy.exc
from flask import Blueprint, request, render_template, redirect, url_for, abort, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy

from models.db.db_meal_time import MealTime
from models.db.db_message_of_the_day_model import MessageOfTheDay
from models.form.message_of_the_day_form import MessageOfTheDayForm
from models.form.set_meal_time_form import SetMealTimeForm
from models.meal_enum import Meal

logistics_routes = Blueprint("logistics_routes", __name__, template_folder='templates/')

db = SQLAlchemy()


@logistics_routes.route("/set_opening_time", methods=["GET", "POST"])
@login_required
def set_opening_time():
    form = SetMealTimeForm()

    if request.method == "GET":
        # get current opening time
        res = MealTime.query.order_by(MealTime.meal).all()

        opening_time = {meal: [(time.is_work_day, time.time_open, time.time_close) for time in times] for meal, times in
                        groupby(res, lambda x: x.meal)}

        return render_template("admin/set_opening_time.html", form=form, opening_time=opening_time)

    elif request.method == "POST":
        # overwrite the database entry
        if form.validate_on_submit():
            try:
                to_edit = db.session.query(MealTime).get((Meal(int(form.meal.data)).name, form.is_work_day.data))

                to_edit.time_open = form.meal_start.data
                to_edit.time_close = form.meal_end.data

                db.session.commit()

                flash("Opening Time Edited", "alert-success")

                return redirect(url_for("logistics_routes.set_opening_time"))
            except sqlalchemy.exc.SQLAlchemyError as e:
                db.session.rollback()
                return abort(500, e)


@logistics_routes.route("/set_message_of_the_day", methods=["GET", "POST"])
@login_required
def set_message_of_the_day():
    form = MessageOfTheDayForm()

    if request.method == "GET":
        return render_template("admin/set_message_of_the_day.html", form=form)

    elif request.method == "POST":
        if form.validate_on_submit():
            new_message = MessageOfTheDay(str(uuid.uuid4()),
                                          form.date.data,
                                          form.message_title.data,
                                          form.message_description.data)

            try:
                db.session.add(new_message)
                db.session.commit()

                flash("Message Added.", "alert-success")

                return redirect(url_for("logistics_routes.set_message_of_the_day"))
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)
            finally:
                db.session.remove()


@logistics_routes.route("/messages_of_the_day/<string:date>", methods=["GET"])
@login_required
def messages_of_the_day(date: str):
    try:
        datetime_object = dateutil.parser.isoparse(date)
    except ValueError as e:
        return abort(400, e)

    # Get all messages
    messages = MessageOfTheDay.query.filter(MessageOfTheDay.date == datetime_object).all()

    return render_template("admin/messages_of_the_day.html", date=datetime_object, messages=messages)


@logistics_routes.route("/delete_message/<string:message_id>", methods=["GET"])
@login_required
def delete_message(message_id: str):
    try:
        message = MessageOfTheDay.query.get(message_id)
        db.session.delete(message)
        db.session.commit()

        if request.referrer:
            flash("Message deleted", "alert-success")

            return redirect(request.referrer)
        else:
            return abort(400, "No referrer, you must interact via the user interface. ")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        return abort(500, e)
