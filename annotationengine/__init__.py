from flask import Flask, jsonify, url_for, redirect, Blueprint
import json
import numpy as np
from emannotationschemas.models import Base
from annotationengine.config import configure_app
from annotationengine.utils import get_instance_folder_path
from annotationengine.api import api_bp
from annotationengine.admin import setup_admin
from annotationengine.views import views_bp
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
import logging
from datetime import date, datetime

__version__ = "2.1.4"


db = SQLAlchemy(model_class=Base)

class AEEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.uint64):
            return int(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def create_app(test_config=None):
    # Define the Flask Object
    app = Flask(__name__,
                instance_path=get_instance_folder_path(),
                static_url_path='/annotation/static',
                instance_relative_config=True)
    app.json_encoder = AEEncoder
    app.config["RESTX_JSON"] = {"cls": AEEncoder}
    logging.basicConfig(level=logging.DEBUG)

    if test_config is None:
        app = configure_app(app)
    else:
        app.config.update(test_config)

    apibp = Blueprint('api', __name__, url_prefix='/annotation/api')
    @apibp.route('/versions')
    def versions():
        return jsonify([2]), 200
        
    with app.app_context():
        api = Api(apibp, title="Annotation Engine API", version=__version__, doc="/doc")
        api.add_namespace(api_bp, path='/v2')
        app.register_blueprint(apibp)
        app.register_blueprint(views_bp)
        db.init_app(app)
        db.create_all()


    @app.route("/health")
    def health():
        return jsonify("healthy"), 200
   
    @app.route("/annotation/")
    def index():
        return redirect("/annotation/views")
    return app
