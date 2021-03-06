from datetime import timedelta
from functools import wraps

import bcrypt
import sqlalchemy.exc
from flask import Blueprint, abort, request, render_template, flash, redirect, url_for
from flask_login import logout_user, login_user, login_required

import config
from app import db
from models.db.db_user_model import User
from models.form.login_form import LoginForm
from models.form.register_form import RegisterForm

login_routes = Blueprint("login_routes", __name__, template_folder='templates/')


@login_routes.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    if request.method == "GET":
        return render_template("admin/login/login.html", form=login_form)
    elif request.method == "POST":
        if login_form.validate_on_submit():
            try:
                user = User.query.get(login_form.username.data)
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)

            if user:
                if bcrypt.checkpw(login_form.password.data.encode(), user.password_hash.encode()):
                    login_user(user=user, remember=True, duration=timedelta(days=1))

                    return redirect(url_for("user_routes.hello_world"))
                else:
                    prompt_incorrect_credential()
                    return redirect(url_for("login_routes.login"))
            else:
                prompt_incorrect_credential()
                return redirect(url_for("login_routes.login"))
        else:
            return render_template("admin/login/login.html", form=login_form)


def prompt_incorrect_credential():
    flash("Either username or password does not match our records, please try again. ", "alert-danger")


def check_register_status(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not config.get_config_from_env().REGISTER_OPEN:
            return abort(403)

        return f(*args, **kwargs)

    return inner


@login_routes.route("/register", methods=["GET", "POST"])
@check_register_status
def register():
    register_form = RegisterForm()

    if request.method == "GET":
        return render_template("admin/login/register.html", form=register_form)

    elif request.method == "POST":
        # Check for duplicated user ID first
        if register_form.validate_on_submit():
            proposed_user_id = register_form.username.data

            try:
                user = User.query.get(proposed_user_id)
            except sqlalchemy.exc.SQLAlchemyError as e:
                return abort(500, e)

            if user:
                # can't have this, kick back
                flash("This username exists, please choose another username. ", "alert-danger")
                return redirect(url_for("login_routes.register"))
            else:
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(register_form.password.data.encode(), salt).decode()

                new_user = User(proposed_user_id, password_hash)

                try:
                    db.session.add(new_user)
                    db.session.commit()

                    flash("Registration Success, please login. ", "alert-success")

                    return redirect(url_for("login_routes.login"))
                except sqlalchemy.exc.SQLAlchemyError as e:
                    return abort(500, e)

        else:
            return render_template("admin/login/register.html", form=register_form)


@login_routes.route('/logout')
@login_required
def logout():
    logout_user()

    flash("Successfully Logged Out", "alert-success")
    return redirect(url_for('user_routes.hello_world'))
