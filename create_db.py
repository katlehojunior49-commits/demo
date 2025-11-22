"""CLI helper to create database tables."""

from sqlalchemy import inspect

from app import create_app, db


def create_database():
    """Initialize the database and echo the available tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        print('Tables in database:', inspector.get_table_names())


if __name__ == '__main__':
    create_database()