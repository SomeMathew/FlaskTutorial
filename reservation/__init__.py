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
