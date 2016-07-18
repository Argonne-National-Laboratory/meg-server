from base64 import b64encode
import binascii
import json
import time
from uuid import uuid4
from urllib.parse import urlencode

from flask import request, Response
from pgpdump.utils import PgpdumpException
import requests
from sqlalchemy.orm import load_only
from sqlalchemy.orm.exc import NoResultFound

from meg import constants
from meg.email import send_revocation_request_email
from meg.exception import BadRevocationKeyException
from meg.pgp import (
    get_user_email_from_key,
    store_revocation_cert as backend_cert_storage,
    verify_trust_level
)
from meg.sks import addkey_to_sks, get_key_by_id, search_key


def send_message_to_phone(app, db, db_models, celery_tasks, action, email_to, email_from):
    # Query the db for the message id. We do not know it because it is dynamically
    # allocated
    committed_message = db_models.MessageStore.query.filter(
        db_models.MessageStore.email_to == email_to
    ).order_by(
        db_models.MessageStore.created_at.desc()
    ).first()
    if not committed_message:
        app.logger.error("Was not able to commit {} message addressed to email {}".format(action, email_to))
        # this shouldn't happen. (But saying this is asking for it to happen)
        return "", 500

    # XXX The logic is a bit overly complex here. If the message is being encrypted it
    # is from the originating client. If the message is being decrypted it is from a 3rd party
    # so the gcm instance id will be associated with email_to. Inevitably we will have bugs here
    # where a message gets sent to the server but maybe someone hasn't registered yet. So...
    # must be refactored and redone. This is getting painful
    if action == "encrypt":
        user_email = email_from
    elif action == "decrypt":
        user_email = email_to
    try:
        instance_id = db_models.GcmInstanceId.query.filter(db_models.GcmInstanceId.email == user_email).one()
    except NoResultFound:
        return "", 404
    celery_tasks.transmit_gcm_id.apply_async(
        (instance_id.instance_id, committed_message.id, committed_message.action)
    )
    return "", 200


def put_message(app, db, db_models, celery_tasks):
    content_type = request.headers["Content-Type"]
    # Things need to be base64 encoded. I want to demand ascii soon
    # but must figure out a way to do it.

    # Check message type
    if "text/plain" not in content_type:
        return "", 415

    app.logger.debug("GETTING HTTP POST PARAMS")

    # Get all variables from HTTP header
    action = request.args['action']  # Can be encrypt, decrypt, or toclient
    email_to = request.args['email_to']
    email_from = request.args['email_from']
    try:
        client_id = request.args['client_id']
    except KeyError:
        client_id = "PHONE"
    try:
        msg_id = request.args['msg_id']
    except KeyError:
        msg_id = "PHONE"

    app.logger.debug("PUT MESSAGE WITH CLIENT ID: {}".format(
        client_id
    ))

    if action not in constants.APPROVED_ACTIONS:
        return "", 400

    # Get data from message and decode
    message = request.data
    if isinstance(message, bytes):
        message = message.decode("ascii")

    # Debugging
    app.logger.debug("Put new message {} from {} in db for {}, from {}, with action {}".format(
        msg_id, client_id, email_to, email_from, action
    ))

    # Put new message in database
    new_message = db_models.MessageStore(client_id, msg_id, email_to, email_from, message, action)
    db.session.add(new_message)
    db.session.commit()

    # Either send to phone or return 200 OK
    if action != "toclient":
        return send_message_to_phone(app, db, db_models, celery_tasks, action, email_to, email_from)
    else:
        return "", 200


def get_message(app, db, db_models):
    # XXX This doesn't cover the case of having multiple messages from the same person to
    # the same recipient but with different subject lines. For now punt on the problem since
    # we don't need to solve it right now
    message_id = request.args.get('message_id')
    email_from = request.args.get("email_from")
    email_to = request.args.get("email_to")
    client_id = request.args.get("client_id")
    msg_id = request.args.get("msg_id")

    app.logger.debug("Get message with id {}, email_from {}, email_to {}.".format(
        message_id, email_from, email_to
    ))
    # Must have either a message id (for use by the app) or email_from and email_to
    # (for use by the client)
    if not message_id and not (email_from and email_to):
        return "", 400

    if message_id:
        app.logger.debug("Get encrypted message with id {}".format(message_id))
        message = db_models.MessageStore.query.filter(
            db_models.MessageStore.id==int(message_id)
        ).first()
    else:
        app.logger.debug("Get email for {} from {}".format(email_to, email_from))
        message = db_models.MessageStore.query.filter(
            (db_models.MessageStore.email_to==email_to) &
            (db_models.MessageStore.action=="toclient") &
            (db_models.MessageStore.email_from==email_from)
        ).first()

    if not message:
        app.logger.warn("Could not find message with id: {} to: {} from: {}".format(
            message_id, email_to, email_from)
        )
        return "", 404

    # Remove the object that we just got.
    db.session.delete(message)
    db.session.commit()
    return Response(
        json.dumps({
            # TODO I can move from here soon and remove the associated_message API
            'message': message.message,
            'email_to': message.email_to,
            'email_from': message.email_from,
        }),
        headers={"Content-Type": "application/octet-stream"},
        status=200
    )


def create_routes(app, db, cfg, db_models, celery_tasks):

    RevocationKey = db_models.RevocationKey
    GcmInstanceId = db_models.GcmInstanceId
    RevocationToken = db_models.RevocationToken

    def _addkey(armored):
        app.logger.debug("Attempt to add key: {}".format(armored))
        return addkey_to_sks(cfg, armored)

    @app.route("{}/addkey".format(cfg.config.meg_url_prefix), methods=["PUT"], strict_slashes=False)
    def addkey():
        armored = request.form["keydata"]
        return _addkey(armored)

    @app.route("{}/getkey/<keyid>".format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def getkey(keyid):
        app.logger.debug("Get key: {}".format(keyid))
        content, status_code = get_key_by_id(cfg, keyid)
        return Response(json.dumps(content), content_type="application/json", status=status_code)

    @app.route("{}/get_trust_level/<our_keyid>/<contact_keyid>".

               format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def get_trust_level(our_keyid, contact_keyid):
        """
        Get the trust level of a contact that we are communicating with

        0: all good and trusted
        1: can be verified through web of trust
        2: untrusted
        """
        app.logger.debug("Get trust level for our: {} contact: {}".format(our_keyid, contact_keyid))
        return str(verify_trust_level(cfg, our_keyid, contact_keyid)), 200

    @app.route("{}/store_revocation_cert".format(cfg.config.meg_url_prefix),
               methods=["PUT"],
               strict_slashes=False)
    def store_revocation_cert():
        """
        Stores a revocation certificate on the machine. The
        certificate will be passed in through form data
        """
        try:
            armored_key = request.form["keydata"]
            app.logger.debug("Store revocation certificate: {}".format(armored_key))
            backend_cert_storage(db, armored_key, RevocationKey)
        except (BadRevocationKeyException, binascii.Error, PgpdumpException) as err:
            return err.args[0], 400
        return "Success", 200

    @app.route("{}/revoke/".format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def revoke_certificate():
        """
        Revoke a users public key certificate
        """
        keyid = request.args["keyid"]
        auth_token = request.args["token"]
        token_result = RevocationToken.query.filter(
            RevocationToken.pgp_keyid_for == keyid
        ).order_by(RevocationToken.created_at.desc())

        # TODO We need to clean up old revocation requests in the DB
        token_row = token_result.first()
        if not token_row:
            return "", 404
        if auth_token != token_row.hex:
            return "", 401
        db.session.delete(token_row)
        db.session.commit()
        if time.time() - int(token_row.created_at.strftime("%s")) > cfg.config.revocation.ttl:
            return "It has been longer than 1 hour since this request was first triggered. Please make a new request to revoke from the phone", 401

        try:
            app.logger.warn("Revoke certificate for key: {}".format(keyid))
            result = RevocationKey.query.options(load_only("armored")).filter(
                RevocationKey.pgp_keyid_for == keyid
            )
            armored = result.distinct().one().armored
        except NoResultFound:
            return "Key {} not found".format(keyid), 404
        _, code = _addkey(armored)
        if code != 200:
            return "We were unable to revoke the token. Please try restarting the revocation process", code

        try:
            instance_id = db_models.GcmInstanceId.query.filter(
                db_models.GcmInstanceId.email == token_row.user_email
            ).one()
        except NoResultFound:
            return "", 404
        celery_tasks.remove_key_data.apply_async((instance_id.instance_id,))
        return "", 200

    @app.route("{}/request_revoke/".format(cfg.config.meg_url_prefix),
               methods=["POST"],
               strict_slashes=False)
    def request_revocation():
        """
        Send a revocation request to the users email address.
        """
        keyid = request.args["keyid"]
        if len(keyid) != 8:
            return "", 400
        content, code = get_key_by_id(cfg, keyid)
        if code != 200:
            return content, code
        hex = uuid4().hex
        user_email = get_user_email_from_key(content['key'])
        revocation = RevocationToken(keyid, hex, user_email)
        db.session.add(revocation)
        db.session.commit()
        content, code = send_revocation_request_email(cfg, keyid, hex, user_email)
        return content, code

    @app.route("{}/search/<search_str>".format(cfg.config.meg_url_prefix),
               methods=["GET"])
    def search(search_str):
        content, status_code = search_key(cfg, search_str)
        if status_code != 200:
            return content, status_code
        return json.dumps(content), status_code

    # XXX This method probably needs some kind of authentication other
    # it would be pretty trivial to perform a denial of service on MEG
    @app.route("{}/gcm_instance_id/".format(cfg.config.meg_url_prefix),
               methods=["PUT"],
               strict_slashes=False)
    def store_gcm_instance_id():
        try:
            instance_id = request.form["gcm_instance_id"]
            phone_number = request.form["phone_number"]
            email = request.form["email"]
            app.logger.debug("Store GCM id: {} for email: {} phone: {}".format(
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

    @app.route("{}/getkey_by_message_id/".format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def get_enc_key_by_message_id():
        """
        Get the public key of the party we want to send an encrypted message to
        """
        try:
            #Get ID from HTTP Header
            message_id = request.args["associated_message_id"]
            app.logger.debug("Get key by msg id: {}".format(message_id))

            #
            message = db_models.MessageStore.query.filter(
                db_models.MessageStore.id == message_id
            ).one()
            content, code = search_key(cfg, message.email_to)

            #Return error code if not 200 OK
            if code != 200:
                return "", code

            id = content["ids"][0]
            content, code = get_key_by_id(cfg, id)

            if code != 200:
                return "", code
        except NoResultFound:
            return "", 404
        else:
            return Response(content['key'], content_type="text/html; charset=ascii", status=200)

    @app.route("{}/decrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def get_decrypted_message():
        """
        Get a decrypted (decrypted by private key) message
        """
        return get_message(app, db, db_models)

    @app.route("{}/decrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["PUT"],
               strict_slashes=False)
    def put_decrypted_message():
        """
        Put a decrypted (decrypted by private key) message on the server
        This message will either be sent to the phone to be encrypted or
        sent back to the client dependant on what we want.
        """
        return put_message(app, db, db_models, celery_tasks)

    @app.route("{}/encrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["GET"],
               strict_slashes=False)
    def get_encrypted_message():
        """
        Get an encrypted message. The mobile device should call this method when
        it has been notified it has a message waiting for it. Upon calling this API the
        server will grab the message from the database and send it to the requester. This
        can also be called by the mail client to receive a recently encrypted message so
        that it can be sent to a recipient. Depending on which party performs the request
        different data will need to be used in the body

        XXX TODO Note how we cannot actually verify the identity of who we are communicating
        with. There needs to be a new feature added that we can ensure we are actually
        communicating with a legitimate client.
        """
        return get_message(app, db, db_models)

    @app.route("{}/encrypted_message/".format(cfg.config.meg_url_prefix),
               methods=["PUT"],
               strict_slashes=False)
    def put_encrypted_message():
        """
        Put an encrypted message onto the server. The mail client should call this method
        when it wants to transmit a message to the mobile app to be decrypted. This will
        trigger an asynchronous request to be placed to the mobile device that notifies
        it that a new message is ready to be received. Once this happens the mobile device
        should then request the message be sent to them. This method is also called when
        we want to send an encrypted message back to the mail client. This will not
        trigger anything but rather the server will just store the message until the
        mail client picks it back up.
        """
        return put_message(app, db, db_models, celery_tasks)
