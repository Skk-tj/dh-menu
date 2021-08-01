from itertools import groupby

import sqlalchemy.exc
from flask import Blueprint, request, render_template, redirect, url_for, abort, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy

from models.db.db_meal_time import MealTime
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
        res = db.session.query(MealTime).order_by(MealTime.meal).all()

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
