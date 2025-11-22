import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions without app so they can be used in factory pattern.
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(test_config=None):
    """Application factory for the Flask app.

    Returns a configured Flask application instance. This follows best practice
    so the app can be created with different configs (tests, prod, etc.).
    """
    app = Flask(__name__, instance_relative_config=False)

    # Ensure the instance folder exists (safer writable location for SQLite file)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        # If instance path can't be created, fall back to current working directory
        pass

    # Base configuration; secrets/DB URL can be overridden through env vars.
    # Default to a SQLite file inside the Flask instance folder unless DATABASE_URL is set
    default_sqlite = 'sqlite:///' + os.path.join(app.instance_path, 'users.db')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', default_sqlite),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Bind extensions to the Flask app.
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints after app creation to avoid circular imports.
    from .routes import main

    app.register_blueprint(main)

    # Ensure database tables exist before serving requests.
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    """Given a user ID stored in the session, return the corresponding User."""
    from .models import User

    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

