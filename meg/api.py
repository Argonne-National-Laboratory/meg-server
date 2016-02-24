from urllib.parse import urlencode

from flask import request
import requests
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import NoResultFound

from meg.pgp import store_revocation_cert as backend_cert_storage, verify_trust_level
from meg.skier import make_get_request, make_skier_request


def create_routes(app, db, cfg, RevocationKey):
    @app.route("/addkey", methods=["PUT"])
    def addkey():
        armored = request.form["keydata"]
        return make_skier_request(
            cfg, requests.put, "addkey?{}".format(urlencode({"keydata": armored}))
        )

    # XXX I don't actually know if we need this API
    #
    # But now that I think more on it we probably will in
    # case we want to sign keys. But let's worry about this later
    @app.route("/getkey/<keyid>", methods=["GET"])
    def getkey(keyid):
        return make_get_request(cfg, "getkey", keyid)

    @app.route("/store_revocation_cert", methods=["PUT"])
    def store_revocation_cert():
        """
        Stores a revocation certificate on the machine. The
        certificate will be passed in through form data
        """
        # XXX TODO error handling
        armored_key = request.form["keydata"]
        backend_cert_storage(db, armored_key, RevocationKey)
        return "Success", 200

    # XXX TODO This needs authentication otherwise everyones certificates
    # could be revoked at will
    @app.route("/revoke_certificate/<keyid>", methods=["POST"])
    def revoke_certificate(keyid):
        """
        Revoke a users public key certificate
        """
        # XXX TODO Error handling
        result = RevocationKey.query.options(load_only("armored")).filter(
            RevocationKey.pgp_keyid_for == keyid
        )
        try:
            armored = result.distinct().one().armored
        except NoResultFound:
            return "Not Found", 404
        # XXX This makes me ask the question. If we revoke a key but then
        # send the unrevoked public key back to skier does Skier handle our
        # certificate as non-revoked again?
        return make_skier_request(
            cfg, requests.post, "addkey?{}".format(urlencode({"keydata": armored}))
        )

    # XXX Search is pretty weak right now on Skier. We might not be able
    # to find keys by email address which is a pretty big deal for us.
    # So lets look into this eventually and figure it out.
    @app.route("/search/<search_str>", methods=["GET"])
    def search(search_str):
        return make_get_request(cfg, "search", search_str)

    @app.route("/get_trust_level/<origin_keyid>/<contact_keyid>", methods=["GET"])
    def get_trust_level(origin_keyid, contact_keyid):
        """
        Get the trust level of a contact that we are communicating with

        0: all good and trusted
        1: can be verified through web of trust
        2: untrusted
        """
        # XXX TODO Error checking
        return str(verify_trust_level(cfg, origin_keyid, contact_keyid)), 200
