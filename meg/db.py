from collections import namedtuple
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

    class GcmInstanceId(db.Model):
        """
        Store phone instance id
        """
        id = db.Column(db.Integer, primary_key=True)
        instance_id = db.Column(db.Text, nullable=False)
        phone_number = db.Column(db.Text, nullable=False)
        email = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, nullable=False)

        def __init__(self, instance_id, phone_number, email):
            self.instance_id = instance_id
            self.phone_number = phone_number
            self.email = email
            self.created_at = datetime.datetime.now()

    class MessageStore(db.Model):
        """
        Stores messages for eventual transmission to client or app
        """
        id = db.Column(db.Integer, primary_key=True)
        action = db.Column(db.VARCHAR(8), nullable=False)
        email_to = db.Column(db.Text, nullable=False)
        email_from = db.Column(db.Text, nullable=False)
        message = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, nullable=False)

        def __init__(self, email_to, email_from, message, action):
            self.action = action
            self.email_to = email_to
            self.email_from = email_from
            self.message = message
            self.created_at = datetime.datetime.now()

    class RevocationToken(db.Model):
        """
        Stores revocation tokens.
        """
        id = db.Column(db.Integer, primary_key=True)
        pgp_keyid_for = db.Column(db.VARCHAR(8), nullable=False)
        hex = db.Column(db.VARCHAR(32), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False)
        user_email = db.Column(db.Text, nullable=False)

        def __init__(self, keyid, hex, user_email):
            self.pgp_keyid_for = keyid
            self.hex = hex
            self.user_email = user_email
            self.created_at = datetime.datetime.now()

    Models = namedtuple('Models', [
        'RevocationKey', 'GcmInstanceId', 'MessageStore', 'RevocationToken'
    ])
    return Models(RevocationKey, GcmInstanceId, MessageStore, RevocationToken)
