import os

import configmaster


def get_yml_config():
    meg_config = os.getenv("MEG_SERVER_CFG", default="config.yml")
    cfg = configmaster.YAMLConfigFile.YAMLConfigFile(meg_config)
    cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))
    return cfg


def configure_app(app):
    cfg = get_yml_config()
    configure_db(app, cfg)
    app.config["MEG_LOCALS"] = cfg


def configure_db(app, cfg):
    uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        **cfg.config.db
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
