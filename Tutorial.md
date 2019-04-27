# A Basic Web Service with Flask

## Table of Content
* [Introduction](#introduction)
    * [About Flask](#about-flask)
    * [Reference](#reference)
    * [Setup](#setup)
* [Application Factory](#application-factory)
* [Database interface with SQLAlchemy](#database-interface-with-sqlalchemy)
* [Blueprint View](#blueprint-view)

## Introduction
This tutorial will walk you through creating a simple web service for a toy reservation system. A working knowledge of 
Python is assumed as a prerequisite. 

This tutorial will use Flask as the basis of the service, SQLAlchemy to interface with the database and SQLite3 for the
database. Python 3.6+ is assumed in this tutorial.

### About Flask
Flask is a microframework for building web services and applications based on Werkzeug. It provides a lightweight 
implementation of the necessary API to build simple or complex web services.
Flask is a non-opinionated framework, it does not impose certain methodologies, libraries or form to build your
application. There is a large number of libraries available to create more advanced applications and it is extensible.

### Reference
This tutorial and the reference code can be found [in this repository](https://github.com/SomeMathew/FlaskTutorial).
Each steps in the tutorial is associated with a branch with the finalized code of that section.

### Setup
#### Environment
In order to prevent polluting the global libraries for *pip* it is preferable to setup a 
[virtual environment (venv)](https://docs.python.org/3.7/library/venv.html) for your project. The virtual environment 
will be created in the root directory of the project `FlaskTutorial/`.

To create and activate the virtual environment, follow the 
[Python's venv documentation](https://docs.python.org/3.7/library/venv.html).

#### Project Layout
The project will be organized according to the following layout:
```
Root directory
├── reservation
│   ├── views
│   │   └── reservations.py
│   ├── __init__.py
│   └── models.py
├── tests
│   ├── test_reservation.py
│   └── test_setup.py
├── requirements.txt
└── setup.py
```

* `reservations/` is the main Python package which contains the Flask application.
* `reservations/views/` contains the blueprints which form the views for the service's API.
* `tests/` contains the automated tests for the system.

#### Packages Installation
**Important**: Before continuing, the virtual environment should be activated (See [Environment](#environment)).

`pip`  will be used to install Flask and SQLAlchemy. Run the following command in the root directory.

```
pip install Flask SQLAlchemy
```
After the installation is complete, Flask and the SQLAlchemy extension will be available to your project.

## Application factory
The first step to creating the service is the method to build and provide the main Flask application object. This 
factory will be used by the `flask run` command line utility or a deployment script to create and configure the Flask 
application.

In the `reservation/` folder, create an `__init__.py` file. This file will be the entry point to the `reservation`
Python package for the service.

**reservation/\_\_init\_\_.py** :
```python
from flask import Flask, jsonify, make_response
from reservation.config import Config

__version__ = '0.0.1'


def create_app(conf: Config = None):
    app = Flask(__name__)

    if conf:
        app.config.from_object(conf)
    else:
        app.config.from_object('reservation.config.DefaultConfig')

    # TODO: DB setup

    @app.route('/version', methods={'GET'})
    def version():
        return jsonify({"service": __name__,
                        "version": __version__})

    @app.errorhandler(400)
    def bad_request(e):
        return make_response(jsonify({"error": True, "code": 400, "msg": str(e)}), 400)

    @app.errorhandler(404)
    def page_not_found(e):
        return make_response(jsonify({"error": True, "code": 404, "msg": str(e)}), 404)

    @app.errorhandler(405)
    def page_not_found(e):
        return make_response(jsonify({"error": True, "code": 405, "msg": str(e)}), 405)

    @app.errorhandler(500)
    def internal_error(e):
        return make_response(jsonify({"error": True, "code": 500, "msg": str(e)}), 500)

    # TODO: Blueprint registrations

    return app
```

You will also need to create a configuration file `config.py` in the `reservation/` folder.
**reservation/config.py** :
```python
class Config:
    pass


class DevConfig(Config):
    DEBUG = True


class DefaultConfig(DevConfig):
    pass
```

This simple application will be runnable as is with the following commands:
```
export FLASK_APP=reservation FLASK_ENV=development
flask run
```
*   The environment variables are necessary for running the application using the flask runner. 
    If on windows, use the `set` command instead.
*   `flask run` will use the factory to instantiate the app and run it on a development WSGI server.

Let's break down this part of the application to get a better idea of what is done by the factory method.

*   The `create_app(conf)` method is the entry point to the Flask application. It will be called by the 
    `flask run` command as described above. It can also be used directly with a custom configuration when testing 
    or deploying using a startup script with a WSGI server such as [chaussette](https://chaussette.readthedocs.io/).

*   `app = Flask(__name__)` Creates the main flask application that will serve the requests to your services. This is 
    the return value of your factory.

*   The `app.config.from_object()` method will configure the application based on the default configuration or what is 
    passed to the factory method. For now, the `DefaultConfig` only sets the DEBUG flag and is set to our `DevConfig` 
    class.

*   `@app.route('/version', methods={'GET'})` is a Python decorator which sets a url route for the decorated method, 
    `version()` in our case. This will be used as an alive check to confirm our service is running.
    
    *   `'/version'` defines the route which will be registered on the WSGI router. This method will be accessible at
        `http://localhost:5000/version` or at your custom url instead of localhost.
    *   `methods={'GET'}` defines for which HTTP method this route will be active. In this case, GET.

*   The `jsonify()` method transforms a Python dict into a JSON response for the given endpoint.

*   The `@app.errorhandler(405)` decorator will be forwarded requests which returns a given failure code and will
    override the response to a custom format. This will be useful later with the `abort()` method in a request handler.


## Database interface with SQLAlchemy
Interfacing with a database, in this case Sqlite, is straightforward with the SQLAlchemy ORM. First SQLAlchemy must
be initialized and models must be defined as the representation of a table row. Second the SQLAlchemy object must be
registered with the Flask application. 

The models and SQLAlchemy object will be defined inside the `models.py` file in the `reservation/` folder.

The service will save a reservation under a person's name and email. No authentication will be considered. A user can
create a new reservation under a given name and email. In this contrived example, the Person model demonstrates the
concept of relationships in SQLAlchemy. 

**reservation/models.py**:
```python
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

```

*   `db = SQLAlchemy()` Creates the SQLAlchemy object, it will be initialized in the application factory below.

*   Each model is defined as a subclass of the db.Model class. To define a column, such as `id` the db.Column object
    must be assigned to a class member of the same name. 

    *   For more details on the Column parameters and field types available see the 
        [Flask-SQLAlchemy documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) and the 
        [SQLAlchemy documentation](https://docs.sqlalchemy.org/en/13/core/metadata.html).

*   To set a relationship between models, first a ForeignKey must be create and an ORM relationship can be created to 
    access the related models directly on the object.

    *   `db.ForeignKey('person.id')` Creates a foreign key to the `person` table and its `id` column.
    
    *   `client = db.relationship(Person, backref='reservations'` creates a relationship in `Reservation` which links
        to the `Person` model. The `backref` parameter will create a link in the `Person` model with a field 
        `reservations` which contains all that person's reservations.
        
*   To initialize the database a click command for the `flask` utility is created with the `@click.command('init-db')` 
    and `@with_appcontext` decorators. The former creates the `flask init-db` command and the latter loads the app
    context from the factory method that will be used. The command will be registered in the application factory below.
    
    *   `db.create_all()` will initialize the tables in the database according to the model definition.

*   While the details are outside of the scope of this tutorial, the `__mapper_args__` configures the `version` field
    for optimistic concurrency control.

The application factory will link the SQLAlchemy object with the application context and will initialize the click 
command. The following code needs to be added to the factory method where the `# TODO: DB Setup` was left.

**reservation/\_\_init\_\_.py**:
```python
import reservation.models as models
models.db.init_app(app)
app.cli.add_command(models.init_db_command)
```
*   `models.db.init_app(app)` links the SQLAlchemy object with the flask's application context.

*   `app.cli.add_command(models.init_db_command` will register the Click `init-db` command.


The database connection also needs to be added to the configuration objects.

**reservation/config.py**
```python
class Config:
    SQLALCHEMY_DATABASE_URI = r"sqlite:///reservation_tutorial.sqlite"
```

At this point the `flask init-db` command can be used to create the table inside the database. 
**Note**: The environment variable for `FLASK_APP=reservation` needs to be set for custom Click command like the
`flask run` command.

## Blueprint View
For the endpoint's view the blueprint facility of Flask will be used. A blueprint is a way to organize the
code into manageable views that deal with a specific concern of the service.

To use a blueprint, first it is created with its associated views, then it is registered with the Flask
application object inside the application factory method.

This tutorial will cover a fairly simple blueprint with views for the following endpoints:
1. Create a new reservation
2. Retrieve all reservations
3. Retrieve a specific reservation by Id.

The blueprint is created in `reservation/views/reservations.py`. An abbreviated portion of the file is shown
here to introduce new concepts. Refer to the source for the complete code. 

**reservation/views/reservations.py**:
```python
...

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')

...

@reservations.route('/<int:reservation_id>', methods={'GET'})
def get_reservation_by_id(reservation_id):
    ...

...

@reservations.route('', methods={'POST'})
def create_reservation():
    """ Creates a new reservation.

    This handler expects a JSON request body with the following fields: name, email, size, time (in ISO format).
    Optionally a note text field can be given as well.

    :return: application/JSON success or failure message { "error" : <bool>, "msg" : <msg>, "code" : <code> }
    """
    ...

    body = request.get_json()
    # Validate fields exists and are not empty
    if not body \
            or not all(field in body for field in fields_req) \
            or not all(val for field, val in body.items() if field in fields_req):
        abort(400, f'Required field must not be null or empty. Required: {", ".join(fields_req)}')

    # Validate the date and time
    ...

    # Validate the party size
    ...

    # Load any existing client or create a new one
    client = Person.query.filter(Person.name.ilike(body['name']), Person.email.ilike(body['email'])).first()
    if not client:
        client = Person(name=body['name'], email=body['email'])

    reservation = Reservation(
        client=client,
        start_datetime=start_datetime,
        party_size=party_size,
        note=body['note'] if ('note' in body and body['note']) else ''
    )

    try:
        db.session.add(reservation)
        db.session.commit()
        return make_response(jsonify({
            'error': False,
            'msg': 'Created',
            'code': 201
        }), 201)
    except SQLAlchemyError:
        abort(500, 'Unable to complete your transaction, try again later.')
```

*   `reservations = Blueprint('reservations', __name__, url_prefix='/reservations')` creates the Blueprint object which
    encapsulates our views for the reservations. 
    
    *   The first argument gives a unique name to the blueprint. 
    *   The second argument `url_prefix='/reservations'` defines the url parameter prefix for all views of this 
        blueprint. Any route defined with the `@reservations.route` decorator will be prefixed by this parameter.
        
*   The `@reservations.route` decorators have an identical meaning to the application route previously defined in
    the application factory. Refer back to the [Application Factory](#application-factory) section.
    
    *   Of note is the addition of a dynamic url parameter in the `get_reservation_by_id(reservation_id)` handler. 
        The route `'/<int:reservation_id>'` will take an int and pass it back as an argument to the parameter of the
        same name in the decorated function. 
        
        In this case the route case be accessed with the url and a reservation id `http://localhost:5000/reservations/1`

*   The `abort()` method is used to create a failure response redirected with a message or exception to the previously 
    defined error handler `@app.errorhandler`in the application factory. The handler will be chosen based on the HTTP
    error code.

*   The `Person.query.filter(..).first()` queries the database for a specific `Person` model. It will return `None` if 
    none can be found. 
    
    For more details on available queries refer to the 
    [SQLAlchemy Query API documentation](https://docs.sqlalchemy.org/en/13/orm/query.html).
    
*   `db.session.add(reservation)` adds a given model to the SQLAlchemy Unit of Work as a new object. 
    It will be committed to the database with the following call `db.session.commit()`. 
    
    Note that SQLAlchemy, in its default configuration, will cascade the commit to related objects. In this case, the
    `client` object will be committed as well if it is a new object, and updated if it has been modified.
    
    It is important to handle any database exception for those method calls and return a server error to the user. 
    It is preferable to not leak any internal details to the user and keep the error message generic. 
    The actual error, in a production environment, should be logged for further analysis.
    
*   The `make_response()` call is implicitly done by the Flask framework, however it defaults to a `200: OK` HTTP code. 
    To override this behaviour, it must be explicitly used, as done above to use the `201: Created` HTTP code. 
    

The last piece of needed code is to register the Blueprint with the flask application. This is done in the application
factory method. This code is self-descriptive, it should be added where the `# TODO: Blueprint registrations` was
previously left.

**reservations/\_\_init\_\_.py**:
```python
from reservation.views.reservations import reservations
app.register_blueprint(reservations)
```

You can now start the service and access the endpoints. The [curl](https://curl.haxx.se/) or 
[Postman](https://www.getpostman.com/) utilities are useful tool to call your services during development. Their use
is outside the scope of this tutorial, however they are well documented.