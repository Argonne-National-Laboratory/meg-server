import json
from urllib.parse import urlencode

from flask import request
import requests
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import NoResultFound

from meg.pgp import store_revocation_cert as backend_cert_storage, verify_trust_level
from meg.skier import make_get_request, make_skier_request


def create_routes(app, db, cfg, db_models, celery_tasks):

    RevocationKey = db_models.RevocationKey
    GcmInstanceId = db_models.GcmInstanceId

    @app.route("{}/addkey".format(cfg.config.meg_url_prefix), methods=["PUT"])
    def addkey():
        armored = request.form["keydata"]
        return make_skier_request(
            cfg, requests.put, "addkey?{}".format(urlencode({"keydata": armored}))
        )

    # XXX I don't actually know if we need this API
    #
    # But now that I think more on it we probably will in
    # case we want to sign keys. But let's worry about this later
    @app.route("{}/getkey/<keyid>".format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def getkey(keyid):
        return make_get_request(cfg, "getkey", keyid)

    @app.route("{}/get_trust_level/<origin_keyid>/<contact_keyid>".
               format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def get_trust_level(origin_keyid, contact_keyid):
        """
        Get the trust level of a contact that we are communicating with

        0: all good and trusted
        1: can be verified through web of trust
        2: untrusted
        """
        # XXX TODO Error checking
        return str(verify_trust_level(cfg, origin_keyid, contact_keyid)), 200

    @app.route("{}/store_revocation_cert".format(cfg.config.meg_url_prefix),
               methods=["PUT"])
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
    #
    # Also this api route should be combined with above. It should just be
    # revocation_cert. The method should also change here to DELETE
    @app.route("{}/revoke_certificate/<keyid>".format(cfg.config.meg_url_prefix),
               methods=["POST"])
    def revoke_certificate(keyid):
        """
        Revoke a users public key certificate
        """
        # XXX TODO Error handling
        try:
            result = RevocationKey.query.options(load_only("armored")).filter(
                RevocationKey.pgp_keyid_for == keyid
            )
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
    @app.route("{}/search/<search_str>".format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def search(search_str):
        return make_get_request(cfg, "search", search_str)

    # XXX This method probably needs some kind of authentication other
    # it would be pretty trivial to perform a denial of service on MEG
    @app.route("{}/gcm_instance_id/".format(cfg.config.meg_url_prefix),
               methods=["PUT"])
    def store_gcm_instance_id():
        try:
            instance_id = request.form["gcm_instance_id"]
            phone_number = request.form["phone_number"]
            email = request.form["email"]
            app.logger.debug("Store GCM iid: {} for email: {} phone: {}".format(
                instance_id, email, phone_number
            ))
            iid = GcmInstanceId.query.filter(GcmInstanceId.email == email).one()
            iid.instance_id = instance_id
        except NoResultFound:
            gcm_instance_id = GcmInstanceId(instance_id, phone_number, email)
            db.session.add(gcm_instance_id)
        finally:
            db.session.commit()
        return "", 200

    @app.route("{}/decrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def get_decrypted_message():
        """
        Get a decrypted (decrypted by private key) message

        Stub method
        """
        return "", 200

    @app.route("{}/decrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["PUT"])
    def put_decrypted_message():
        """
        Put a decrypted (decrypted by private key) message on the server
        This message will be picked up by the client eventually

        Stub method
        """
        return "", 200

    @app.route("{}/encrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def get_encrypted_message():
        """
        Get an encrypted message. The mobile device should call this method when
        it has been notified it has a message waiting for it. Upon calling this API the
        server will grab the message from the database and send it to the requester.

        Note how we cannot actually verify the identity of who we are communicating
        with. There needs to be a new feature added that we can ensure we are actually
        communicating with a legitimate client.
        """
        message_id = request.form['message_id']
        app.logger.debug("Get encrypted message with id {}".format(message_id))
        try:
            message = db_models.MessageStore.query.filter(
                db_models.MessageStore.id==int(message_id)
            ).one()
        except NoResultFound:
            # Should never happen IRL. But testing yes
            app.logger.warn("Could not find message with id {}".format(message_id))
            return "", 404

        app.logger.debug(
            "Transmitting message id {} for user with email {}".format(message.id, message.email)
        )
        # XXX Is a rollback clause necessary here?
        db.session.delete(message)
        db.session.commit()
        return json.dumps({"message": message.message}), 200

    @app.route("{}/encrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["PUT"])
    def put_encrypted_message():
        """
        Put an encrypted message onto the server. The mail client should call this method
        when it wants to transmit a message to the mobile app to be decrypted. This will
        trigger an asynchronous request to be placed to the mobile device that notifies
        it that a new message is ready to be received. Once this happens the mobile device
        should then request the message be sent to them. The data in the form for this
        method should look like

        {"email": "foo@bar.com", "message": <encrypted message here>}
        """
        email = request.form['email']
        message = request.form['message']
        app.logger.debug("Put new encrypted message for {}".format(email))
        new_message = db_models.MessageStore(email, message)
        db.session.add(new_message)
        db.session.commit()
        committed_message = db_models.MessageStore.query.filter(
            db_models.MessageStore.email == email
        ).order_by(
            db_models.MessageStore.created_at.desc()
        ).first()
        if not committed_message:
            app.logger.error("Was not able to commit encrypted message for user with email {}".format(email))
            return "", 500  # this shouldn't happen
        try:
            instance_id = db_models.GcmInstanceId.query.filter(db_models.GcmInstanceId.email == email).one()
        except NoResultFound:
            return "", 404
        celery_tasks.transmit_gcm_id.apply_async(
            (instance_id.instance_id, committed_message.id, "decrypt")
        )
        return "", 200
