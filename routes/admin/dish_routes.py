import uuid

import sqlalchemy.exc
from flask import Blueprint, render_template, redirect, url_for, abort, request, flash
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy

from models.db.db_dish_model import Dish
from models.form.add_dish_form import AddDishForm
from models.meal_enum import Meal

dish_routes = Blueprint("dish_routes", __name__, template_folder='templates/')

db = SQLAlchemy()


@dish_routes.route('/add_dish', methods=['GET', 'POST'])
@login_required
def add_dish():
    form = AddDishForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # add dish to the database
            try:
                meal_string = Meal(int(form.for_which_meal.data)).name
            except ValueError as e:
                return abort(400, e)

            form.uuid = uuid.uuid4()

            new_dish = Dish(form.uuid,
                            form.dish_name.data.capitalize(),
                            form.is_vegan.data,
                            form.is_vegetarian.data,
                            form.is_halal.data,
                            form.is_gluten_free.data,
                            form.annotation.data,
                            meal_string)

            try:
                db.session.add(new_dish)
                db.session.commit()

                flash("A dish has been successfully added.", "alert-success")
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)

            return redirect(url_for("dish_routes.manage_dish"))
        else:
            return render_template("admin/dish/add_dish.html", form=form)
    elif request.method == "GET":
        return render_template("admin/dish/add_dish.html", form=form)


@dish_routes.route('/manage_dish', methods=['GET'])
@login_required
def manage_dish():
    # make database query to get all the dishes
    try:
        dishes = Dish.query.order_by(Dish.dish_name).all()
    except sqlalchemy.exc.SQLAlchemyError as e:
        return abort(500, e)

    # display all the dishes
    return render_template("admin/dish/manage_dish.html", dishes=dishes)


@dish_routes.route('/delete_dish/<string:dish_id>')
@login_required
def delete_dish(dish_id):
    try:
        dish_to_delete = Dish.query.get(dish_id)
        db.session.delete(dish_to_delete)
        db.session.commit()

        flash("A dish has been successfully deleted. ", "alert-success")

        return redirect(url_for("dish_routes.manage_dish"))
    except sqlalchemy.exc.SQLAlchemyError as e:
        return abort(500, e)


@dish_routes.route('/edit_dish', methods=["GET", "POST"])
@login_required
def edit_dish():
    if "dish_id" in request.args:
        dish_id = request.args["dish_id"]
    else:
        return abort(400)

    form = AddDishForm()

    if request.method == "GET":
        try:
            dish_to_edit = Dish.query.get(dish_id)

            form.annotation.data = dish_to_edit.annotation
            form.for_which_meal.data = str(Meal[dish_to_edit.for_which_meal].value)

            return render_template("admin/dish/edit_dish.html", form=form, dish=dish_to_edit)
        except sqlalchemy.exc.SQLAlchemyError as e:
            return abort(500, e)
        except KeyError as e:
            return abort(400, e)
    elif request.method == "POST":
        if form.validate_on_submit():
            try:
                dish_to_edit = db.session.query(Dish).get(dish_id)

                dish_to_edit.dish_name = form.dish_name.data
                dish_to_edit.is_vegan = form.is_vegan.data
                dish_to_edit.is_vegetarian = form.is_vegetarian.data
                dish_to_edit.is_halal = form.is_halal.data
                dish_to_edit.is_gluten_free = form.is_gluten_free.data
                dish_to_edit.annotation = form.annotation.data
                dish_to_edit.for_which_meal = Meal(int(form.for_which_meal.data)).name

                db.session.commit()

                flash("The dish has been edited successfully. ", "alert-success")

                return redirect(url_for("dish_routes.manage_dish"))
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)
            except ValueError as e:
                return abort(400, e)
