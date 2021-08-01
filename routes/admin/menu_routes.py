import datetime
import json
import uuid
from itertools import groupby

import dateutil.parser
import isoweek
import sqlalchemy.exc
from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy

from models.db.db_days_published import DaysPublished
from models.db.db_dish_model import Dish
from models.db.db_menu_for_meal_model import MenuForMeal
from models.db.db_sections_model import Sections
from models.db.db_publish_version import PublishVersion
from models.form.build_menu_select_form import BuildMenuSelectForm
from models.form.publish_menu_select_form import PublishMenuSelectForm
from models.meal_enum import Meal
from util.util import get_opening_time_for_date_meal

menu_routes = Blueprint("menu_routes", __name__, template_folder='templates/')

db = SQLAlchemy()


def _get_menu_status_for_date(date: datetime.datetime) -> dict:
    meals = list(Meal)

    full_menu = {}

    for meal in meals:
        # get the dictionary for this meal in this day
        menu_db_result = (db.session
                          .query(MenuForMeal.section_id, MenuForMeal.dish_id)
                          .join(Sections, Sections.section_id == MenuForMeal.section_id)
                          .filter(MenuForMeal.date == date)
                          .filter(MenuForMeal.for_which_meal == meal.name)
                          .order_by(MenuForMeal.section_id).all())

        menu_for_meal = {}

        try:
            for section, dishes in groupby(menu_db_result, lambda x: x[0]):
                menu_for_meal[section] = True if [dish[1] for dish in dishes] else False
        except AttributeError:
            pass

        full_menu[meal] = menu_for_meal

    return full_menu


def _get_full_menu_for_date_meal(date: datetime.datetime, meal: Meal) -> dict:
    menu_db_result = (db.session
                      .query(MenuForMeal.id,
                             Sections,
                             Dish)
                      .join(Sections).join(Dish)
                      .filter(MenuForMeal.date == date)
                      .filter(MenuForMeal.for_which_meal == meal.name)
                      .order_by(Sections.section_name).all())

    menu_for_meal = {}

    try:
        for section, dishes in groupby(menu_db_result, lambda x: x[1]):
            menu_for_meal[section] = [dish[2] for dish in dishes]  # the 2nd item is all the Dish columns
    except AttributeError:
        pass

    return menu_for_meal


def _get_sections_dict() -> dict:
    sections_dict = {}

    for meal in list(Meal):
        sections_dict[meal] = [(_.section_name, _.section_id)
                               for _ in (db.session
                                         .query(Sections.section_name,
                                                Sections.section_id)
                                         .filter(Sections.section_for_which_meal == meal.name)
                                         .order_by(Sections.section_name).all())]

    return sections_dict


def _put_menu_dict_to_db(menu_dict, datetime_object: datetime.datetime, meal: Meal):
    for section, dishes in menu_dict.items():
        for dish in dishes:
            item_id = uuid.uuid4()

            try:
                new_menu_item = MenuForMeal(id=item_id,
                                            date=datetime_object,
                                            for_which_meal=meal.name,
                                            section_id=section,
                                            dish_id=dish)

                db.session.add(new_menu_item)
                db.session.commit()
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)
            except ValueError as e:
                return abort(400, e)


def _update_publish_version() -> uuid.UUID:
    """
    Update the public version of the menu.
    :return: The new version in UUID format.
    """
    version = db.session.query(PublishVersion).first()
    version.id = uuid.uuid4()
    db.session.commit()

    return version.id


@menu_routes.route("/build_menu", methods=['GET', 'POST'])
@login_required
def build_menu_select():
    form = BuildMenuSelectForm()

    if request.method == "GET":
        return render_template("admin/menu/build_menu_select.html", form=form)

    elif request.method == "POST":
        if form.validate_on_submit():
            return redirect(url_for("menu_routes.build_menu_this_day",
                                    date=form.date.data,
                                    meal=form.meal.data))


@menu_routes.route("/build_menu/<string:date>/<int:meal>", methods=['GET', 'POST'])
@login_required
def build_menu_this_day(date: str, meal: int):
    try:
        datetime_object = dateutil.parser.isoparse(date)
        meal_enum = Meal(meal)
    except ValueError as e:
        return abort(400, e)

    if request.method == "GET":
        # check if menu has been built for this date
        is_menu_item_present = (db.session
                                .query(MenuForMeal)
                                .filter(MenuForMeal.date == datetime_object)
                                .filter(MenuForMeal.for_which_meal == meal_enum.name).all())

        if is_menu_item_present:
            return redirect(url_for("menu_routes.edit_menu", date=date, meal=meal))

        # get corresponding sections for this meal
        sections = (db.session
                    .query(Sections)
                    .filter(Sections.section_for_which_meal == meal_enum.name)
                    .order_by(Sections.section_name))

        list_of_dishes = (db.session
                          .query(Dish)
                          .filter(Dish.for_which_meal == meal_enum.name)
                          .order_by(Dish.dish_name))

        return render_template("admin/menu/build_menu.html",
                               date=datetime_object.strftime("%A %b %-d, %Y"),
                               meal=meal_enum.name,
                               sections=sections,
                               list_of_dishes=list_of_dishes)

    elif request.method == "POST":
        # process values from json strings to python objects
        menu_dict = {key: json.loads(value) for (key, value) in request.form.items()}

        _put_menu_dict_to_db(menu_dict, datetime_object, meal_enum)

        flash("Menu Edited", "alert-success")
        return redirect(url_for("menu_routes.manage_menu_for_week", week=datetime_object.strftime("%Y-W%W")))


@menu_routes.route("/manage_menu", methods=['GET', 'POST'])
@login_required
def manage_menu_select():
    form = PublishMenuSelectForm()

    if request.method == "GET":
        return render_template("admin/menu/manage_menu_select.html", form=form)

    elif request.method == "POST":
        if form.validate_on_submit():
            return redirect(url_for("menu_routes.manage_menu_for_week", week=form.week.data))


@menu_routes.route("/manage_menu/<string:week>")
@login_required
def manage_menu_for_week(week: str):
    try:
        week_obj = isoweek.Week.fromstring(week)
    except ValueError as e:
        return abort(400, e)

    menu_for_week = []

    for d in [week_obj.day(x) for x in range(7)]:
        menu = _get_menu_status_for_date(d)
        menu_for_week.append(
            {"is_published": True if DaysPublished.query.get(d.isoformat()) else False, "date": d, "menu": menu})

    sections = _get_sections_dict()

    return render_template("admin/menu/manage_menu.html",
                           menu_for_week=menu_for_week,
                           sections=sections)


@menu_routes.route("/preview_menu/<string:date>/<int:meal>/")
@login_required
def preview_menu_for_date_meal(date: str, meal: int):
    try:
        datetime_object = dateutil.parser.isoparse(date)

        meal_enum = Meal(meal)
    except ValueError as e:
        return abort(400, e)

    menu = _get_full_menu_for_date_meal(datetime_object, meal_enum)

    opening_time = get_opening_time_for_date_meal(datetime_object, meal_enum)

    return render_template("admin/menu/preview_menu_for_date_meal.html",
                           date=datetime_object,
                           meal_string=meal_enum.name,
                           menu=menu,
                           opening_time=opening_time)


@menu_routes.route("/manage_sections")
@login_required
def manage_sections():
    sections_dict = _get_sections_dict()

    return render_template("admin/menu/manage_sections.html", sections_dict=sections_dict)


@menu_routes.route("/publish/<string:date>")
@login_required
def publish_date(date: str):
    try:
        datetime_object = dateutil.parser.isoparse(date)
    except ValueError:
        return abort(400)

    new_publish = DaysPublished(date=datetime_object, is_published=True)

    try:
        db.session.add(new_publish)
        db.session.commit()

        _update_publish_version()

        flash(f"Published menu for {datetime_object.strftime('%A %b %-d, %Y')}", "alert-success")

        if request.referrer:
            return redirect(request.referrer)
        else:
            abort(400, "No referrer, you must interact via the user interface. ")
    except sqlalchemy.exc.SQLAlchemyError as e:
        return abort(500, e)


@menu_routes.route("/undo_publish/<string:date>")
@login_required
def undo_publish_date(date: str):
    try:
        datetime_object = dateutil.parser.isoparse(date)
    except ValueError:
        return abort(400)

    res = db.session.query(DaysPublished).get(datetime_object.isoformat())

    if res:
        try:
            db.session.delete(res)
            db.session.commit()

            _update_publish_version()

            flash(f"Unpublished menu for {datetime_object.strftime('%A %b %-d, %Y')}", "alert-success")

            if request.referrer:
                return redirect(request.referrer)
            else:
                return abort(400, "No referrer, you must interact via the user interface. ")
        except sqlalchemy.exc.SQLAlchemyError as e:
            db.session.rollback()
            return abort(500, e)
    else:
        return abort(500)


@menu_routes.route("/edit_menu/<string:date>/<int:meal>", methods=["GET", "POST"])
@login_required
def edit_menu(date: str, meal: int):
    try:
        datetime_object = dateutil.parser.isoparse(date)

        meal_enum = Meal(meal)
    except ValueError as e:
        return abort(400, e)

    if request.method == "GET":
        # prepare the date string for template
        date_string = datetime_object.strftime("%A %b %-d, %Y")

        # get corresponding sections for this meal
        sections = (db.session
                    .query(Sections)
                    .filter(Sections.section_for_which_meal == meal_enum.name)
                    .order_by(Sections.section_name).all())

        # get dishes in sections
        menu = _get_full_menu_for_date_meal(datetime_object, meal_enum)

        # get the all dishes for this type of meal
        total_list_of_dishes = (db.session
                                .query(Dish)
                                .filter(Dish.for_which_meal == meal_enum.name)
                                .order_by(Dish.dish_name).all())

        dishes_in_sections = [item for sublist in menu.values() for item in sublist]

        remaining_dishes = [item for item in total_list_of_dishes if item not in dishes_in_sections]

        return render_template("admin/menu/edit_menu.html", date=date_string, sections=sections, menu=menu,
                               list_of_dishes=remaining_dishes, meal=meal_enum.name)

    elif request.method == "POST":
        menu_dict = {key: json.loads(value) for (key, value) in request.form.items()}

        # delete all the previous menu entries
        try:
            (db.session.query(MenuForMeal)
             .filter(MenuForMeal.date == date)
             .filter(MenuForMeal.for_which_meal == meal_enum.name)
             .delete())
            db.session.commit()

        except sqlalchemy.exc.SQLAlchemyError as e:
            db.session.rollback()
            return abort(500, e)

        # put the new menu into the db
        _put_menu_dict_to_db(menu_dict, datetime_object, meal_enum)

        flash("Menu Edited", "alert-success")
        return redirect(
            url_for("menu_routes.manage_menu_for_week", week=datetime_object.strftime("%Y-W%W")))


@menu_routes.route("/reset_menu/<string:date>/<int:meal>")
@login_required
def reset_menu(date: str, meal: int):
    try:
        datetime_object = dateutil.parser.isoparse(date)

        meal = Meal(meal)
    except ValueError as e:
        return abort(400, e)

    try:
        (db.session
         .query(MenuForMeal)
         .filter(MenuForMeal.date == datetime_object.isoformat())
         .filter(MenuForMeal.for_which_meal == meal.name).delete())

        db.session.commit()

        flash(f"Reset menu for {datetime_object.strftime('%A')}'s {meal.name}", "alert-success")

        if request.referrer:
            return redirect(request.referrer)
        else:
            return abort(400, "No referrer, you must interact via the user interface. ")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        return abort(500, e)
