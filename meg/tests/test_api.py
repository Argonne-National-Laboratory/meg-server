from base64 import b64encode
import json
from io import StringIO
import os
from unittest.mock import patch

from flask import Flask
from flask.ext.testing import TestCase
from nose.tools import eq_

from meg.app import create_app as make_app
from meg.cfg import configure_app


DECRYPT = "decrypt"
EMAIL1 = "foo@bar.com"
EMAIL2 = "bin@baz.org"
ENCRYPT = "encrypt"
GCM_IID = "foobar"
MESSAGE1 = b64encode(b'\x85\x01\x0c\x03\xd3\xd6\x13o0\x01-=\x01\x07\xffN\xb7Q\x0e \x9cZx\xc6\xb4f$\xf9\xd8\xf5\xff\xc2a\xc9\xad5\xdbu.Ri\xf9E\x10\xcf\xc2\xf8\xe4b\xe9\x16\xcf\x1f\xf5\xfe\xf8\xda\x8f\xeb\xaf\xd2;\x1dx\x8a\xc3\x0bz\x93\xdc=\xa0\x8d! \xf8\xf3\x92\x83 \xa9\xd3t\xf3\x81\x8e\x1e!\xb8\xafRB{6\x18\x83{\x8b\xe6*\xac\xd373\x93\x1f/a|\xb4A\xccodO\xff\x80\r\xa4\xa0#\x84q\x0fn\xcd\x04\x82j\xa0\xee\xb8Z\xfe\xda\xb5E\xf9\x95\x19iI|\x14+4F\xa5\xa8\xae\xa9\n"$q\xdb\x97j\'V\xb3s\x1aE\xb1\x04\xda\xf9]hI\x85\xe4\xc4ao\x99\xc8ZA\xd5\x88\xbf\xe8\xd0\x1d\xd9&\x1e\xb8\xec\x85;\xc0OlA\xd02\xd3\xd6\xfc\x07\xf4m\x1a\x0c\x1c\xde\xa2\xc6 \x0cOMkA\x9dF\x9d*\x9e\xd7\x8c\xeb\x9a\xdb\x81p\xa6\xecF\x9eo!\\\x10\xd1\xdd1{\xa6G\xfd\xcc\x10\xe7P\xde4\xe9Id9\xa3\xf5\x0cl\xe6\x8c4\x9aN+fn\x14\xa9M\xfe\xda\xc9)\x9e#[\xa3\xf2\x90\xa6K\xfa3|\x8d#\xf2\xec\x004?\xcd\xce\xd5:\xda\x94\xf6\xc8\xda\x81y\xfaB<\xc0a,a\xabe\xe8\x95\x08').decode("ascii")
MESSAGE2 = b64encode(b'\x85\x01\x0c\x03\xd3\xd6\x13o0\x01-=\x01\x07\xff\x7f<\xcbg\x94&q8\xff\xf0\xe6\xb7j\xd6\xde~\xcdWG\x08>\xfa\xb9:\x13\x86\x91\x1c\x7f\xf4\x06\xe8\x01dP\x1a4\xf1\x85G\x8c\xdd\xdc\xdaX\x1d\x8d\x13\xd2d\x1f\xfc&\x1f\xec\x88\xd5\xcf\x142\x0b2\xb4\xe3PFHR`qQ\x1d\xa4\xf5\xddp\x10\xd1\xfc\x06@\xe6<\xc0\x11\xe6+\xe4\xaeJ\xf6D\x90\xa1\x15U\xda\xaa\xed\xac,{\x16\xe2\xdd\x9bt\t\x8ef\xe2c\x1c*E\xf1gO.\xfbw\xf187\t2\x9b\xe8\x1e\x7f8\x16\xc1w\x1c\x17\xe6\x0bri\xe9\xab\x83\xb9)\\\xcf5\xa9A\xa0\xd3G\xb3.\xe8G\xd9\xfe:\x8f\xe0\x1e\xcb\x15\xd1%\xc7\x07\x87 \x94\xd6\x8dmWT\xce\xfc\xc4\xd7}4\xbfB\x8dN\xf2\x85\xd8`\x87/Y\x06?\xbec\xfa*\xe6@\x9f\xd5\x83\x85\xd9\x98\xb0\x120h\xa2\xfd\xa6\xc9\xca\xd4!\xebj\xc3B\xc1\xbdo\\\xd4\xb4\xa05`\xb2\xfc\xa0\xa7*Q\xa6,Z@L`\xb6]&\xa4Q\xca\xa5\x1d\xd9E\xa4\x98\xc9"\x18e\x97]\x95\xc6\x14\xea\xbc|n}\xee-\x8e\x1aq4\x1fT\xb1\xcea\xdd\xbf\x7f\xdc\xb8\xf2\x80\x00\xda\x1f[').decode("ascii")
PHONE_NUMBER = "5551112222"
PUB_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2

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
FzCQNmQ1
=3GLU
-----END PGP PUBLIC KEY BLOCK-----"""

TO_CLIENT = "toclient"


class MockResponse(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json():
        # Hopefully we provided our content as a dictionary
        return content


class TestMEGAPI(TestCase):
    def create_app(self):
        with patch("meg.app.create_celery_routes") as celery_routes:
            self.celery_routes = celery_routes
            app, self.db, self.models, _ = make_app(debug=True, testing=True)
            self.cfg, _ = configure_app(app, True, True)
            return app

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_addkey(self):
        mock_content = "blah"
        with patch("meg.api.requests") as mock_requests:
            mock_requests.post.return_value = MockResponse(200, mock_content)
            response = self.client.put("/addkey", data={"keydata": PUB_KEY})
            eq_(response.data.decode(), mock_content)
            eq_(response.status_code, 200)

    def test_getkey(self):
        with patch("meg.skier.requests") as mock_requests:
            mock_requests.get.return_value = MockResponse(200, PUB_KEY)
            response = self.client.get("/getkey/11111A")
            eq_(response.data.decode(), PUB_KEY)
            eq_(response.status_code, 200)

    def test_get_trust_level_for_level_zero_trust(self):
        web = {
            "http://localhost:5000/api/v1/keyinfo/1111B": MockResponse(
                200, '{"sigs": {"1111B": [["1111B"], ["1111A"]]}}'
            )
        }
        side_effect = lambda a: web[a]
        with patch("meg.skier.requests") as mock_requests:
            mock_requests.get.side_effect = side_effect
            response = self.client.get("/get_trust_level/1111A/1111B")
            eq_(response.status_code, 200)
            eq_(response.data.decode(), "0")

    def test_get_trust_level_for_level_one_trust(self):
        web = {
            "http://localhost:5000/api/v1/keyinfo/1111B": MockResponse(
                200, '{"sigs": {"1111B": [["1111B"], ["1111C"]]}}'
            ),
            "http://localhost:5000/api/v1/keyinfo/1111C": MockResponse(
                200, '{"sigs": {"1111C": [["1111C"], ["1111A"]]}}'
            )
        }
        side_effect = lambda a: web[a]
        with patch("meg.skier.requests") as mock_requests:
            mock_requests.get.side_effect = side_effect
            response = self.client.get("/get_trust_level/1111A/1111B")
            eq_(response.status_code, 200)
            eq_(response.data.decode(), "1")

    def test_store_instance_id(self):
        instance_id = "foobar"
        data = {"gcm_instance_id": instance_id, "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)
        item = self.models.GcmInstanceId.query.filter(self.models.GcmInstanceId.id == 1).one()
        eq_(item.instance_id, instance_id)
        eq_(item.phone_number, PHONE_NUMBER)
        eq_(response.status_code, 200)

    def test_store_instance_id_on_missing_iid(self):
        data = {"phone_number": "5551112323"}
        response = self.client.put("/gcm_instance_id/", data=data)
        eq_(response.status_code, 400)

    def test_store_instance_id_on_same_device(self):
        # I want the behavior to be that we update the existing record.
        # it will just help with eventual code writing
        data = {"gcm_instance_id": "foobar", "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)
        eq_(response.status_code, 200)
        final_iid = "bazbar"
        data = {"gcm_instance_id": final_iid, "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)
        eq_(response.status_code, 200)
        items = self.models.GcmInstanceId.query.filter(self.models.GcmInstanceId.phone_number == PHONE_NUMBER).all()
        eq_(len(items), 1)
        eq_(items[0].instance_id, final_iid)
        eq_(items[0].phone_number, PHONE_NUMBER)

    def test_put_encrypted_message_success_with_decrypt(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)

    def test_put_encrypted_message_success_with_encrypt(self):
        # XXX This test has a weird premise. It wants to encrypt an already encrypted message.
        # I think this is showing that we have made our logic too complex in the message putter.
        # So it reminds me we need more error checking to ensure we are not trying to encrypt an
        # already encrypted email.
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": ENCRYPT}
        self.put_message_with_gcm_addition(data, 200, "/decrypted_message/", EMAIL2)
        self.celery_routes().transmit_gcm_id.apply_async.assert_called_with((GCM_IID, 1, "encrypt"))

    def test_put_encrypted_message_error_no_email_from(self):
        """
        Test PUT for /encrypted_message/ by not adding email_from
        """
        data = {"email_to": EMAIL1, "action": DECRYPT, "message": MESSAGE1}
        self.put_encrypted_message_with_gcm_addition(data, 400, "")

    def test_put_encrypted_message_ensure_we_send_right_one(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)

        self.celery_routes().transmit_gcm_id.apply_async.assert_called_with((GCM_IID, 1, "decrypt"))

        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE2, "action": DECRYPT}
        self.put_encrypted_message(data, 200)
        self.celery_routes().transmit_gcm_id.apply_async.assert_called_with((GCM_IID, 2, "decrypt"))

    def test_put_encrypted_message_error_bad_action(self):
        data = {"email_to": EMAIL1, "action": DECRYPT, "message": MESSAGE1, "action": "blah"}
        self.put_encrypted_message_with_gcm_addition(data, 400, "")

    def test_put_encrypted_message_without_phone_action(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        eq_(self.celery_routes().transmit_gcm_id.apply_async.call_count, 1)
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": TO_CLIENT}
        self.put_encrypted_message(data, 200)

    def put_encrypted_message_with_gcm_addition(self, message_put_data, expected_code, linked_email):
        """
        Helper method for setting up a GCM instance id. Mirrors process of a phone registering
        with the server. Then send an encrypted message to the server.
        """
        self.put_message_with_gcm_addition(
            message_put_data, expected_code, "/encrypted_message/", linked_email
        )

    def put_message_with_gcm_addition(self, message_put_data, expected_code, uri, linked_email):
        gcm_data = {
            "gcm_instance_id": GCM_IID, "phone_number": PHONE_NUMBER, "email": linked_email
        }
        response = self.client.put("/gcm_instance_id/", data=gcm_data)
        self.put_message(message_put_data, expected_code, uri)

    def put_encrypted_message(self, put_data, expected_code):
        """
        Helper method for putting an encrypted message on the server.

        Not really necessary per se after refactor but keeping around for legacy purpose
        """
        self.put_message(put_data, expected_code, "/encrypted_message/")

    def put_message(self, put_data, expected_code, uri):
        file = StringIO(put_data["message"])
        del put_data["message"]
        response = self.client.put(
            uri,
            query_string=put_data,
            input_stream=file,
            headers={"Content-Type": "text/plain; charset=us-ascii"}
        )
        eq_(response.status_code, expected_code)

    def test_get_encrypted_message_success_with_message_id(self):
        """
        Put a new message in the db to be decrypted. This then calls GET with a message id

        Eventually mock the phone calling to grab the message for decryption
        """
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        # We're kinda cheating here because we know the id
        response = self.client.get("/encrypted_message/?message_id={}".format(1))
        eq_(response.status_code, 200)
        eq_(response.data.decode("ascii"),
            json.dumps({
                "message": MESSAGE1,
                "email_to": EMAIL1,
                "email_from": EMAIL2
            }))

    def test_get_decrypted_email_to_client(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": TO_CLIENT}
        self.put_encrypted_message(data, 200)
        response = self.client.get("/encrypted_message/?email_from={}&email_to={}".format(EMAIL2, EMAIL1))
        eq_(response.status_code, 200)
        eq_(response.data.decode("ascii"),
            json.dumps({
                "message": MESSAGE1,
                "email_to": EMAIL1,
                "email_from": EMAIL2,
            }))

    def test_get_encrypted_message_without_message_id_or_all_email_info1(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        response = self.client.get("/encrypted_message/", data={"email_from": EMAIL2})
        eq_(response.status_code, 400)

    def test_get_encrypted_message_without_message_id_or_all_email_info2(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        response = self.client.get("/encrypted_message/", data={"email_to": EMAIL2})
        eq_(response.status_code, 400)

    def test_getkey_by_message_id(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        with patch("meg.skier.requests") as mock_requests:
            # invariably we just need the public key... and I'm a little bit too
            # lazy to do this with a side_effect atm
            mock_requests.get.return_value = MockResponse(200, bytes(json.dumps({"key": PUB_KEY, "ids": ["1234"]}), "utf8"))
            response = self.client.get("/getkey_by_message_id/?associated_message_id=1")
            eq_(response.status_code, 200)
            eq_(response.data, bytes(PUB_KEY, "ascii"))

    def test_getkey_by_message_id_err_no_msg(self):
        with patch("meg.skier.requests") as mock_requests:
            mock_requests.get.return_value = MockResponse(200, json.dumps({"key": PUB_KEY, "ids": ["1234"]}))
            response = self.client.get("/getkey_by_message_id/?associated_message_id=1")
            eq_(response.status_code, 404)

    def test_getkey_by_message_id_with_side_effect(self):
        # The ultimate we can do when testing this function.
        def side_effect(arg):
            keyid = "111"
            return {
                "{}/api/v1/search/{}".format(self.cfg.config.keyservers[0], EMAIL1): MockResponse(200, bytes(json.dumps({"ids": [keyid]}), "utf8")),
                "{}/api/v1/getkey/{}".format(self.cfg.config.keyservers[0], keyid): MockResponse(200, bytes(json.dumps({"key": PUB_KEY}), "utf8")),
            }[arg]

        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message_with_gcm_addition(data, 200, EMAIL1)
        with patch("meg.skier.requests") as mock_requests:
            mock_requests.get.side_effect = side_effect
            response = self.client.get("/getkey_by_message_id/?associated_message_id=1")
            eq_(response.status_code, 200)
            eq_(response.data, bytes(PUB_KEY, "ascii"))
