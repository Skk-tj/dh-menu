import envparse
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import TestConfig, ProductionConfig

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    flask_app = Flask(__name__)

    if envparse.env.bool("FLASK_DEBUG", default=True):
        flask_app.config.from_object(TestConfig())
    else:
        flask_app.config.from_object(ProductionConfig())

    uri = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = uri

    # Routes Init
    from routes.admin.dish_routes import dish_routes
    from routes.admin.menu_routes import menu_routes
    from routes.admin.login_routes import login_routes
    from routes.api.menu_api import menu_api
    from routes.user_routes import user_routes
    from routes.admin.logistics_routes import logistics_routes

    flask_app.register_blueprint(menu_routes)
    flask_app.register_blueprint(user_routes)
    flask_app.register_blueprint(dish_routes)
    flask_app.register_blueprint(logistics_routes)
    flask_app.register_blueprint(menu_api)
    flask_app.register_blueprint(login_routes)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    login_manager.init_app(flask_app)

    login_manager.login_view = "login_routes.login"
    login_manager.login_message = u"Please login to access this page. "
    login_manager.login_message_category = "alert-info"
    login_manager.session_protection = "strong"

    @flask_app.errorhandler(400)
    def bad_request(e):
        return render_template('error/400.html', error_content=e), 400

    @flask_app.errorhandler(404)
    def not_found(e):
        return render_template('error/404.html', error_content=e), 404

    @flask_app.errorhandler(500)
    def internal(e):
        return render_template('error/500.html', error_content=e), 500

    @flask_app.after_request
    def apply_security(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if not envparse.env.bool("FLASK_DEBUG", default=False):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @flask_app.context_processor
    def inject():
        return dict(is_register_open=flask_app.config["REGISTER_OPEN"], version_string=flask_app.config["VERSION_STRING"])

    @login_manager.user_loader
    def load_user(user_id):
        from models.db.db_user_model import User
        return User.query.get(user_id)

    return flask_app


if __name__ == '__main__':
    app = create_app()

    app.jinja_env.auto_reload = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
