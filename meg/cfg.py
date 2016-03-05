import os

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
    return cfg


def configure_db(app, cfg, testing):
    if not testing:
        uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **cfg.config.db
        )
    else:
        uri = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
