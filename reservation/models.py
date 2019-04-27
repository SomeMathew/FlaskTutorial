import click
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

db = SQLAlchemy()


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        "version_id_col": version
    }


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    client = db.relationship(Person, backref='reservations')

    start_datetime = db.Column(db.DateTime, nullable=True)
    party_size = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=True)

    __mapper_args__ = {
        "version_id_col": version
    }


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Database created!')
