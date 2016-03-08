"""
meg.app
~~~~~~~

Create a flask app
"""
from flask import Flask

from meg.api import create_routes
from meg.cfg import configure_app
import meg.db
from meg.stalks import create_celery_routes


def create_app(testing=False, debug=False):
    app = Flask(__name__)
    cfg, celery = configure_app(app, testing, debug)
    celery_tasks = create_celery_routes(celery, cfg)
    db = meg.db.create_db(app)
    db_models  = meg.db.generate_models(db)
    db.create_all()
    create_routes(app, db, cfg, db_models, celery_tasks)
    return app, db, db_models, celery
