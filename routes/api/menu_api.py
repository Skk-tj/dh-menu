import datetime
import zoneinfo

import dateutil.parser
import isoweek
from flask import Blueprint, abort, jsonify

from app import db
from models.db.db_publish_version_model import PublishVersion
from util.util import user_get_menu_for_week, user_get_menu_for_date

menu_api = Blueprint("menu_api", __name__, url_prefix="/api")


@menu_api.route("full_menu")
def full_menu_this_week():
    today = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/Vancouver"))

    this_week: isoweek.Week = isoweek.Week(*(today.isocalendar()[:2]))

    full_menu = user_get_menu_for_week(this_week)

    for day in full_menu:
        day["date"] = day["date"].isoformat()

        for meal in day["menu"]:
            meal["open_time"] = meal["open_time"].isoformat()
            meal["close_time"] = meal["close_time"].isoformat()

    return jsonify(full_menu), 200


@menu_api.route("full_menu_for_week/<string:week>")
def full_menu_for_week(week: str):
    try:
        week_obj = isoweek.Week.fromstring(week)
    except ValueError as e:
        return abort(400, e)

    full_menu = user_get_menu_for_week(week_obj)

    for day in full_menu:
        day["date"] = day["date"].isoformat()

        for meal in day["menu"]:
            meal["open_time"] = meal["open_time"].isoformat()
            meal["close_time"] = meal["close_time"].isoformat()

    return jsonify(full_menu), 200


@menu_api.route("full_menu_for_day/<string:date>")
def full_menu_for_day(date: str):
    try:
        datetime_object = dateutil.parser.isoparse(date)
    except ValueError as e:
        return abort(400, e)

    menu_for_this_day = user_get_menu_for_date(datetime_object)

    for meal in menu_for_this_day:
        meal["open_time"] = meal["open_time"].isoformat()
        meal["close_time"] = meal["close_time"].isoformat()

    return jsonify(menu_for_this_day), 200


@menu_api.route("version")
def get_version():
    version = PublishVersion.query.first()

    return jsonify(version.id), 200
