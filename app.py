import envparse
from flask import Flask, render_template
from flask_login import LoginManager

import config

from models.db.db_days_published import db as days_published_db
from models.db.db_dish_model import db as dish_db
from models.db.db_meal_time import db as opening_time_db
from models.db.db_menu_for_meal_model import db as menu_for_meal_db
from models.db.db_sections_model import db as sections_db
from models.db.db_user_model import User

from routes.admin.dish_routes import db as dish_routes_db
from routes.admin.dish_routes import dish_routes

from routes.admin.logistics_routes import db as logistics_routes_db
from routes.admin.logistics_routes import logistics_routes

from routes.admin.menu_routes import db as menu_routes_db
from routes.admin.menu_routes import menu_routes

from routes.admin.login_routes import login_routes

from routes.api.menu_api import db as menu_api_db
from routes.api.menu_api import menu_api

from routes.user_routes import db as user_routes_db
from routes.user_routes import user_routes

config = config.get_config_from_env()

app = Flask(__name__)

app.config['SECRET_KEY'] = config.FLASK_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
uri = config.DATABASE_URL
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False

# DB Model Init
dish_db.init_app(app)
menu_for_meal_db.init_app(app)
days_published_db.init_app(app)
sections_db.init_app(app)
opening_time_db.init_app(app)

# Routes DB Init
menu_routes_db.init_app(app)
dish_routes_db.init_app(app)
logistics_routes_db.init_app(app)
user_routes_db.init_app(app)
menu_api_db.init_app(app)

# Routes Init
app.register_blueprint(menu_routes)
app.register_blueprint(user_routes)
app.register_blueprint(dish_routes)
app.register_blueprint(logistics_routes)
app.register_blueprint(menu_api)
app.register_blueprint(login_routes)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login_routes.login"
login_manager.login_message = u"Please login to access this page. "
login_manager.login_message_category = "alert-info"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.errorhandler(400)
def bad_request(e):
    return render_template('error/400.html', error_content=e), 400


@app.errorhandler(404)
def not_found(e):
    return render_template('error/404.html', error_content=e), 404


@app.errorhandler(500)
def internal(e):
    return render_template('error/500.html', error_content=e), 500


@app.after_request
def apply_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if not envparse.env.bool("FLASK_DEBUG", default=False):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.context_processor
def inject():
    return dict(is_register_open=config.REGISTER_OPEN, version_string=config.VERSION_STRING)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
