from logging.config import dictConfig
import os

from celery import Celery
import configmaster


def get_yml_config():
    file_dir = os.path.dirname(__file__)
    meg_config = os.getenv("MEG_SERVER_CFG", default="{}/config.yml".format(file_dir))
    cfg = configmaster.YAMLConfigFile.YAMLConfigFile(meg_config)
    meg_default_config = os.getenv("MEG_SERVER_DEFAULT_CFG", default="{}/config.default.yml".format(file_dir))
    cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile(meg_default_config))
    return cfg


def configure_app(app, testing, debug):
    app.debug = debug
    app.config["TESTING"] = testing
    cfg = get_yml_config()
    configure_db(app, cfg, testing)
    celery = create_and_configure_celery(app)
    dictConfig(cfg.config.logging.dump())
    return cfg, celery


def configure_db(app, cfg, testing):
    if not testing:
        uri = "postgresql://{user}:{password}@{host}:{port}/{database}?client_encoding=utf8".\
            format(**cfg.config.db)
    else:
        uri = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri


def create_and_configure_celery(app):
    broker_url = "sqla+{}".format(app.config["SQLALCHEMY_DATABASE_URI"])
    result_backend = broker_url.replace("sqla+", "db+")
    celery = Celery("tasks", backend=result_backend, broker=broker_url)
    return celery
