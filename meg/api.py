from urllib.parse import urlencode

from flask import Blueprint, request
import requests

from meg.pgp import store_revocation_cert as backend_cert_storage, verify_trust_level
from meg.skier import make_get_request, make_skier_request


def create_routes(app, db, cfg, RevocationKey, Signature):
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


    @app.route("/revoke_certificate/<keyid>", methods=["POST"])
    def revoke_certificate(keyid):
        """
        Revoke a users public key certificate
        """
        # XXX This method is really just a stub
        armored_key = get_revocation_cert()
        return make_skier_request(
            cfg, requests.post, "addkey?{}".format(urlencode({"keydata": armored_key}))
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
        return str(verify_trust_level(cfg, Signature, origin_keyid, contact_keyid)), 200
