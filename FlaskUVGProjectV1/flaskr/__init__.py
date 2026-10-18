import os

from flask import (
    Flask,
    send_from_directory,
    request
)
from flask_cors import CORS
from .extensions import db, migrate
from . import models

def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*"
            },
            r"/assets/specimens/*": {
                "origins": "*"
            }
        }
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.environ["DATABASE_URL"]
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"],
        MASTER_DELETE_PASSWORD=os.environ[
            "MASTER_DELETE_PASSWORD"
        ]
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    if not app.config.get("TESTING", False):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 1800
        }

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        base_dir = os.path.dirname(__file__)  # flaskr
        assets_path = os.path.join(base_dir, "assets")

        return send_from_directory(assets_path, filename)

    @app.after_request
    def add_unity_webgl_headers(response):

        path = request.path

        if path.startswith(
            "/static/exhibition/Build/"
        ):

            if path.endswith(".unityweb"):

                response.headers[
                    "Content-Encoding"
                ] = "gzip"

                if ".wasm." in path:
                    response.headers[
                        "Content-Type"
                    ] = "application/wasm"

                elif ".framework.js." in path:
                    response.headers[
                        "Content-Type"
                    ] = "application/javascript"

                elif ".data." in path:
                    response.headers[
                        "Content-Type"
                    ] = "application/octet-stream"

        return response

    from . import public
    app.register_blueprint(public.bp)

    from . import exhibition
    app.register_blueprint(exhibition.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import users
    app.register_blueprint(users.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)

    from . import requests
    app.register_blueprint(requests.bp) 

    from . import inventory
    app.register_blueprint(inventory.bp)

    from . import movements
    app.register_blueprint(movements.bp)

    from . import api
    app.register_blueprint(api.bp)

    db.init_app(app)
    migrate.init_app(app, db)

    return app
