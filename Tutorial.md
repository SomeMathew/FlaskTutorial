# A Basic Web Service with Flask

## Table of Content
* [Introduction](#introduction)
    * [About Flask](#about-flask)
    * [Reference](#reference)
    * [Setup](#setup)
* [Application Factory](#application-factory)
* [Database interface with SQLAlchemy](#database-interface-with-sqlalchemy)

## Introduction
This tutorial will walk you through creating a simple web service for a toy reservation system. A working knowledge of 
Python is assumed as a prerequisite. 

This tutorial will use Flask as the basis of the service, SQLAlchemy to interface with the database and SQLite3 for the
database. Python 3.6+ is assumed in this tutorial.

### About Flask
Flask is a microframework for building web services and applications based on werkzeug. It provides a lightweight 
implementation of the necessary API to build simple or complex web services.
Flask is a non-opinionated framework, it does not impose certain methodologies, libraries or form to build your
application. There is a large number of libraries available to create more advanced applications and is easily extensible.

### <a name="reference"> Reference </a>
This tutorial and the reference code can be found [in this repository](https://github.com/SomeMathew/FlaskTutorial).
Each steps in the tutorial is associated with a Git tag with the finalized code of that section.

### Setup
#### Environment
In order to prevent polluting the global libraries for *pip* it is preferable to setup a 
[virtual environment (venv)](https://docs.python.org/3.7/library/venv.html) for your project. The virtual environment will be
created in the root directory of the project `FlaskTutorial/`.

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

This simple application will be runnable as his with the following commands:
```
export FLASK_APP=reservation FLASK_ENV=development
flask run
```
*   The environment variables are necessary for running the application using the flask runner. 
    If on windows, use the `set` command instead.
*   `flask run` will instantiate use the factory to create the app and run it on a development WSGI server.

Let's break down this part of the application to get a better idea of what is done by the factory method.

*   The `create_app(conf)` method is the entry point to the Flask application. It will be called by the 
    `flask run` command as described above. It can also be used directly with a custom configuration when testing 
    or deploying using a startup script with a WSGI server such as [chaussette](https://chaussette.readthedocs.io/).

*   `app = Flask(__name__)` Creates the main flask application that will serve the requests to your services. This is the
    return value of your factory.

*   The `app.config.from_object()` method will configure the application based on the default configuration or what is passed 
    to the factory method. For now, the `DefaultConfig` only sets the DEBUG flag and is set to our `DevConfig` class.

*   `@app.route('/version', methods={'GET'})` is a Python decorator which sets a url route for the decorated function, 
    `version()` in our case. This will be used as an alive check and confirm our service is running.
    
    *   `'/version'` defines the route which will be registered on the WSGI router. This method will be accessible at
        `http://localhost:5000/version` or at your custom url instead of localhost.
    *   `methods={'GET'}` defines for which HTTP method this route will be active. In this case, GET.

*   The `jsonify()` method transforms a Python dict into a JSON response for the given endpoint.

*   The `@app.errorhandler(405)` decorator will be forwarded requests which returns a given failure code and will
    override the response to a custom format. This will be useful later with the `abort()` method in a request handler.
