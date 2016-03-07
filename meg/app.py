"""
meg.app
~~~~~~~

Create a flask app
"""
from flask import Flask

from meg.api import create_routes
from meg.cfg import configure_app
import meg.db


def create_app(testing=False, debug=False):
    app = Flask(__name__)
    cfg = configure_app(app, testing, debug)
    db = meg.db.create_db(app)
    models  = meg.db.generate_models(db)
    db.create_all()
    create_routes(app, db, cfg, models.RevocationKey, models.GcmInstanceId)
    return app, db, models
