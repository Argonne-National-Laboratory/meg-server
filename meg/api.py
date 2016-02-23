from urllib.parse import urlencode

from flask import Blueprint, request
import requests

from meg.pgp import store_revocation_cert as backend_cert_storage


def getkey_or_search(cfg, api, arg):
    urn = "{}/{}".format(server_url,  api, arg)
    return make_skier_request(cfg, requests.get, urn)


def make_skier_request(cfg, func, urn):
    """
    Get skier specific info. Just act as a thin proxy.
    """
    keyservers = cfg.config.keyservers
    for server_url in keyservers:
        r = func("{}/api/v1/{}".format(server_url, urn))
        if r.status_code != 200:
            continue
        return r.content, 200
    else:
        return r.content, r.status_code


def create_routes(app, db, cfg, RevocationKey):
    @app.route("/getkey/<keyid>", methods=["GET"])
    def getkey(keyid):
        return getkey_or_search(cfg, "getkey", keyid)


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


    @app.route("/revoke_certificate", methods=["POST"])
    def revoke_certificate():
        """
        Revoke a users public key certificate
        """
        armored_key = get_revocation_cert()
        return make_skier_request(
            cfg, requests.post, "addkey?{}".format(urlencode({"keydata": armored_key}))
        )


    @app.route("/search/<search_str>", methods=["GET"])
    def search(search_str):
        return getkey_or_search(cfg, "search", search_str)


    @app.route("/get_trust_level/<origin_keyid>/<contact_keyid>", methods=["GET"])
    def get_trust_level(origin_keyid, contact_keyid):
        """
        Get the trust level of a contact that we are communicating with

        0: all good and trusted
        1: can be verified through web of trust
        2: untrusted
        """
        pass
