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
        keyalgo = db.Column(db.Integer, nullable=False)
        created = db.Column(db.DateTime, nullable=False)
        expires = db.Column(db.DateTime, nullable=True)
        length = db.Column(db.Integer, nullable=False)
        armored = db.Column(db.Text, nullable=False)
        signatures = db.relationship("Signature", backref="revocation_key")

        def __init__(self, keyalgo, created, expires, length, armored, key_id):
            self.keyalgo = keyalgo
            self.created = created
            self.expires = expires
            self.length = length
            self.armored = armored
            sig = Signature()
            sig.pgp_keyid = key_id
            sig.sigtype = 32  # Stands for 'Key revocation signature'
            # XXX Do we want to store revocation certs for subkeys?? Probably not for now.
            sig.key_sfp_for = key_id
            self.signatures.append(sig)  # XXX Are there ever multiple?


    class Signature(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        pgp_keyid = db.Column(db.String(16), nullable=False)
        sigtype = db.Column(db.Integer)
        key_sfp_for = db.Column(db.String(16))
        key_id = db.Column(db.Integer, db.ForeignKey("revocation_key.id"))

    return RevocationKey, Signature
