import datetime
import zoneinfo

import isoweek
from flask import Blueprint, render_template, abort
from flask_sqlalchemy import SQLAlchemy

from util.util import user_get_menu_for_week, user_get_messages_for_week

user_routes = Blueprint("user_routes", __name__, template_folder='templates/')

db = SQLAlchemy()


@user_routes.route('/')
def hello_world():
    today = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Vancouver"))

    this_week: isoweek.Week = isoweek.Week(*(today.isocalendar()[:2]))

    # get menu for days
    menu = user_get_menu_for_week(this_week, db, today.weekday())

    is_empty = [day["is_published"] for day in menu]

    messages = user_get_messages_for_week(this_week)

    return render_template("user/index.html", menu=menu, is_empty=is_empty, this_week=this_week, messages=messages)


@user_routes.route("/<string:week>")
def view_week(week):
    try:
        week_obj = isoweek.Week.fromstring(week)
    except ValueError as e:
        return abort(400, e)

    menu = user_get_menu_for_week(week_obj, db)

    is_empty = [day["is_published"] for day in menu]

    messages = user_get_messages_for_week(week_obj)

    return render_template("user/index.html", menu=menu, is_empty=is_empty, this_week=week_obj, messages=messages)


@user_routes.route('/panic')
def panic():
    abort(404, "I'm not a teapot. ")
