import isoweek
from flask import Blueprint, abort, jsonify
from flask_sqlalchemy import SQLAlchemy

from util.util import user_get_menu_for_week
from models.db.db_publish_version import PublishVersion

menu_api = Blueprint("menu_api", __name__, url_prefix="/api")

db = SQLAlchemy()


@menu_api.route("full_menu_for_week/<string:week>")
def full_menu_for_week(week: str):
    try:
        week_obj = isoweek.Week.fromstring(week)
    except ValueError as e:
        return abort(400, e)

    full_menu = user_get_menu_for_week(week_obj, db)

    for day in full_menu:
        day["date"] = day["date"].isoformat()

        for meal in day["menu"]:
            meal["open_time"] = meal["open_time"].isoformat()
            meal["close_time"] = meal["close_time"].isoformat()

    return jsonify(full_menu), 200


@menu_api.route("version")
def get_version():
    version = PublishVersion.query.first()

    return jsonify(version.id), 200
