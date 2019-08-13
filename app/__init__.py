import os

from flask import Flask


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

from .api.patients import PatientAPI
from .api.physicians import PhysicianAPI
from .api.clinic import ClinicAPI


# instantiate extensions


db = SQLAlchemy()
migrate = Migrate()
api = Api()

# Import after instantianting the db object
from .api.prescriptions import PrescriptionAPI


def create_app(env=None):

    from config import config

    # instantiate app
    app = Flask(__name__)

    # set app config
    if not env:
        env = os.environ.get("FLASK_ENV", "default")
        app.config.from_object(config[env])
        # config[env].configure(app)
    else:
        app.config.from_object(config[env])
    # set up extensions
    for ext in (db, migrate):
        if ext == migrate:
            ext.init_app(app, db)
        else:
            ext.init_app(app)

    # register Resource for Flask-Restful
    register_resource(app)

    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
        "logs/iClinicChallenge.log", maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Prescriptions API startup")

    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.INFO)
    app.logger.addHandler(syslog_handler)

    return app


# Function to register Resources for the Api
def register_resource(app):
    api.app = app
    api.add_resource(PatientAPI, "/v2/patient/<int:patient_id>")
    api.add_resource(PhysicianAPI, "/v2/physician/<int:physician_id>")
    api.add_resource(ClinicAPI, "/v2/clinic/<int:clinic_id>")
    api.add_resource(PrescriptionAPI, "/v2/prescriptions")
