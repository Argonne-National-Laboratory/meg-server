"""
app
~~~

Create a flask app
"""
from flask import Flask


def initialize(app):
    from meg.api import meg_api
    from cfg import configure_app
    import db
    configure_app(app)
    app.register_blueprint(meg_api)
    db.db.create_all()


app = Flask(__name__)
initialize(app)
