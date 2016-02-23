import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY


def create_db(app):
    db = SQLAlchemy(app)
    return db


def generate_models(db):
    class RevocationKey(db.Model):
        """
        The model for a PGP Revocation Key.
        """
        id = db.Column(db.Integer, primary_key=True)
        created = db.Column(db.DateTime, nullable=False)
        expires = db.Column(db.DateTime, nullable=True)
        length = db.Column(db.Integer, nullable=False)
        armored = db.Column(db.Text, nullable=False)
        pgp_keyid_for = db.Column(db.String(16), nullable=False)

        def __init__(self, created, expires, length, armored, key_id_for):
            self.created = created
            self.expires = expires
            self.length = length
            self.armored = armored
            self.pgp_keyid_for = key_id_for

    return RevocationKey
