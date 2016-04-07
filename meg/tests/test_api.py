import os
from unittest.mock import patch

from flask import Flask
from flask.ext.testing import TestCase
from nose.tools import eq_

from meg.app import create_app as make_app
from meg.db import generate_models


DECRYPT = "decrypt"
EMAIL1 = "foo@bar.com"
EMAIL2 = "bin@baz.org"
ENCRYPT = "encrypt"
MESSAGE1 = "asjhfkjsahfdkjshf"
MESSAGE2 = "kasfsbfkjsagdfj"
PHONE_NUMBER = "5551112222"
PUB_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2

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
FzCQNmQ1
=3GLU
-----END PGP PUBLIC KEY BLOCK-----"""

REVOCATION_ID = "CAE99D9C"
REVOCATION_CERT = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2
Comment: A revocation certificate should follow

iQElBCABCAAPBQJWy706CB0AZm9vYmFyAAoJEOeC9ljK6Z2cYFQH/1o7l8Zz+LVH
YT8txGwVLnN84rxEAAjMcoiOrsHkKKGCxu6qcK6Zt5RvgpLN9pr283P2WaTRxagX
qeD0DC2I+TNNEpn/tHILcpV0Q9CtgY30Hvyzfm1pd9HwKobB8nxt2pVJGlEfhTZy
ssMb8seIsAl5Ccws6XQn540Ua+KTnKesKLo6P6KoBfLG36mUF0sViQyuOms4NBFg
N964TRBCFixaaUUf5nnlT1PQcW1+bvFvrIMjVeuxeDzOCfaPxZjhavieWMQDvmgy
PVCiOvA+YdWNojLWKiwaocWrsrn0tW9fJ0ugk2Wz/sIfo08Z7tKSnbirF2Otg6UL
KtJtLoGaduI=
=qITv
-----END PGP PUBLIC KEY BLOCK-----"""
REVOCATION_CERT2 = """-----BEGIN PGP PUBLIC KEY BLOCK-----
BCPG v@RELEASE_NAME@
mQENBFcEh6QBCAC+VC+/esqm76EkxvPc1rBNuUKDlKgJnXd+3fHAu4uYW+Vu5Z0B
MYHTBtFTpNuRJLrWBUDhqvhamzWf8rYASUBhv747clp1CW9hdaJ6EDkFG8DpKZG7
H2wSqzD3LiXPmCvxXWgKX1aajjpVsH2Z20whZG6yMqs6KMhakik8FItYe9fKTWNc
dqLJFh8O+p6qKYdAZ0I4PDVPGDuYO18G10IX22TAgj5rDi2lwYyBl6O+q2BaDfdM
ovmEam8JpqEjvyGdwa0WpcozQoDroLQTBooLAE/5WH5R/Lkxk3+xU6CBs16nJxiH
DonAoQNguUurIWbjcGNw0+LRJTIWkRLjoDp/ABEBAAGJAWUEIAECAE8FAlcEh6QX
jIABdOQTBIyxljzQW7VHMaCuGxNjN8UwnQNhdXRvbWF0aWNhbGx5IGdlbmVyYXRl
ZCByZXZvY2F0aW9uIGNlcnRpZmljYXRlAAoJEDGgrhsTYzfFzlkH/20RIIOEtap3
h04zARvtbEnA2doPqkjbaAiQCh4m1cbFAq39i/mMYJlylVbOphebyuvXI11YiaQ9
TqvlhWHF6PNA/h2ISBlZXD5UqOgwcjEt7PN5in/XaxlPbDABEWnZkvRTaZiqz+Vn
i2By16afpdH1aLmW9zJtSUapoHiRAMWq4tGXL/8KP+2YDmF3tgLJOC8K8AB+WpmL
Oact5Xf76OEo9Xy2yuE3h7bhpac5MINyDTMIwa/Y+JOM2dbu/a1BVkB2cFxZPe8P
zh0jFi1UB3uWFQ3/opfm0znZecrNWIE4U+ZesD2ShLJeRvd6reMIn0QB+1qLgUU6
WV0PkIhC8K60D2ZvbyBiYXIgYUBiLmNvbYkBHAQTAQIABgUCVwSHpAAKCRAxoK4b
E2M3xTftB/4rv9rUBbaDnEImQfmbxJXtnEuXfo8UiunYlMJcCXGePvTCDJAY1LMJ
TiVVJj9+38GSuDo+h3/gx3KaJotO5D+Z75O2tYTLfTktjv9I0LTdekH4RLPzV8aU
l8j0qSld1jSslUhr46sPgyBVkcgP+CrRuq6wG18xI+rxVdgU+TCPryMIsWErPsDi
ewQ29FtgwJ/KkBWtv7QVEMR3tuQQMFH7rGgfWMZS51DSDYwGRq2exoEau1MWVzxP
7hTQfhliNG4GZPI0R6Powh2L+G41jKMn7fC+BU7np+6V8cQIEM4VUPSeOv9TV+t4
t8LdAeusaEu+31ZK5/lOhxQnQlnKzsDi
=vySY
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
            return app

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_revocation_storage1(self):
        """
        This test is not a guarantee that the DB interactions will work
        correctly but at least validates that something on the code
        side of things is not horribly wrong
        """
        response = self.client.put("/store_revocation_cert", data={"keydata": REVOCATION_CERT})
        eq_(response.status_code, 200)

    def test_revocation_storage2(self):
        """
        This test is not a guarantee that the DB interactions will work
        correctly but at least validates that something on the code
        side of things is not horribly wrong
        """
        response = self.client.put("/store_revocation_cert", data={"keydata": REVOCATION_CERT2})
        eq_(response.status_code, 200)

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

    def test_revoke_cert(self):
        self.test_revocation_storage1()
        mock_content = "blah"
        with patch("meg.api.requests") as mock_requests:
            mock_requests.post.return_value = MockResponse(200, mock_content)
            response = self.client.post("/revoke_certificate/{}".format(REVOCATION_ID))
            eq_(response.status_code, 200)
            eq_(response.data.decode(), mock_content)

    def test_revoke_cert_with_no_key(self):
        response = self.client.post("/revoke_certificate/11111A")
        eq_(response.status_code, 404)

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
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": "fgsdkhjfgashjdfbsbdfkkjsg", "action": DECRYPT}
        self.put_encrypted_message(data, 200)

    def test_put_encrypted_message_success_with_encrypt(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": "fgsdkhjfgashjdfbsbdfkkjsg", "action": ENCRYPT}
        self.put_encrypted_message(data, 200)

    def test_put_encrypted_message_error_no_email_from(self):
        """
        Test PUT for /encrypted_message/ by not adding email_from
        """
        data = {"email_to": EMAIL1, "action": DECRYPT, "message": MESSAGE1}
        self.put_encrypted_message(data, 400)

    def test_put_encrypted_message_ensure_we_send_right_one(self):
        iid = "foobar"
        data = {"gcm_instance_id": iid, "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)

        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        response = self.client.put("/encrypted_message/", data=data)
        eq_(response.status_code, 200)
        self.celery_routes().transmit_gcm_id.apply_async.assert_called_with((iid, 1, "decrypt"))

        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE2, "action": DECRYPT}
        response = self.client.put("/encrypted_message/", data=data)
        eq_(response.status_code, 200)
        self.celery_routes().transmit_gcm_id.apply_async.assert_called_with((iid, 2, "decrypt"))

    def test_put_encrypted_message_error_bad_action(self):
        data = {"email_to": EMAIL1, "action": DECRYPT, "message": MESSAGE1, "action": "blah"}
        self.put_encrypted_message(data, 400)

    def test_put_encrypted_message_without_phone_action(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": TO_CLIENT}
        self.put_encrypted_message(data, 200)
        eq_(self.celery_routes().transmit_gcm_id.apply_async.call_count, 0)

    def put_encrypted_message(self, put_data, expected_code):
        data = {"gcm_instance_id": "foobar", "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)

        response = self.client.put("/encrypted_message/", data=put_data)
        eq_(response.status_code, expected_code)

    def test_get_encrypted_message_success_with_message_id(self):
        """
        Put a new message in the db to be decrypted. This then calls GET with a message id

        Eventually mock the phone calling to grab the message for decryption
        """
        iid = "foobar"
        data = {"gcm_instance_id": iid, "phone_number": PHONE_NUMBER, "email": EMAIL1}
        response = self.client.put("/gcm_instance_id/", data=data)

        MESSAGE1 = "asjhfkjsahfdkjshf"
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        response = self.client.put("/encrypted_message/", data=data)
        eq_(response.status_code, 200)
        # We're kinda cheating here because we know the id
        response = self.client.get("/encrypted_message/", data={"message_id": 1})
        eq_(response.status_code, 200)
        eq_(response.json["message"], MESSAGE1)
        eq_(response.json["email_from"], EMAIL2)
        response = self.client.get("/encrypted_message/", data={"message_id": 1})
        eq_(response.status_code, 404)

    def test_get_decrypted_email_to_client(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": TO_CLIENT}
        self.put_encrypted_message(data, 200)
        response = self.client.get("/encrypted_message/", data={"email_from": EMAIL2, "email_to": EMAIL1})
        eq_(response.status_code, 200)
        eq_(response.json["email_to"], EMAIL1)
        eq_(response.json["email_from"], EMAIL2)
        eq_(response.json["message"], MESSAGE1)
        eq_(response.json["action"], TO_CLIENT)

    def test_get_encrypted_message_without_message_id_or_all_email_info1(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message(data, 200)
        response = self.client.get("/encrypted_message/", data={"email_from": EMAIL2})
        eq_(response.status_code, 400)

    def test_get_encrypted_message_without_message_id_or_all_email_info2(self):
        data = {"email_to": EMAIL1, "email_from": EMAIL2, "message": MESSAGE1, "action": DECRYPT}
        self.put_encrypted_message(data, 200)
        response = self.client.get("/encrypted_message/", data={"email_to": EMAIL2})
        eq_(response.status_code, 400)
