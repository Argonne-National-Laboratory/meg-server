from flask import Blueprint


meg_api = Blueprint("meg_api", __name__)

@meg_api.route("/getkey/<keyid>", methods=["GET"])
def getkey(keyid):
    pass


@meg_api.route("/store_revocation_cert", methods=["POST"])
def store_revocation_cert():
    pass


@meg_api.route("/search/<search_str>", methods=["GET"])
def search(search_str):
    pass


@meg_api.route("/get_trust_level/<keyid>", methods=["GET"])
def get_trust_level(keyid):
    pass
