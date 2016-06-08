from unittest.mock import patch

from flask.ext.testing import TestCase
from nose.tools import eq_

from meg.app import create_app as make_app
from meg.cfg import configure_app
from meg.constants import EMAIL_HTML

EMAIL1 = "foo@bar.com"
GCM_IID = "foobar"
PHONE_NUMBER = "5551112222"
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
# This second cert isn't working because it doesn't have a newline
# following the BCPG bit so we can write a test case around it.
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
TOKEN = "0x123"


class TestMEGRevocationAPI(TestCase):
    def create_app(self):
        #with patch("meg.app.create_celery_routes") as celery_routes:
        #self.celery_routes = celery_routes
        app, self.db, self.models, self.celery_routes = make_app(debug=True, testing=True)
        self.cfg, _ = configure_app(app, True, True)
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

    def test_revocation_storage_with_multiples(self):
        self.test_revocation_storage1()
        self.test_revocation_storage1()
        results = self.models.RevocationKey.query.filter(
            self.models.RevocationKey.armored == REVOCATION_CERT
        ).all()
        eq_(len(list(results)), 1)

    def test_revocation_storage_with_malformed_cert_binascii_error(self):
        # Add an additional newline to the start of the cert
        pos = REVOCATION_CERT2.find("PGP")
        cert = REVOCATION_CERT2[:pos] + "\n" + REVOCATION_CERT2[pos:]
        response = self.client.put("/store_revocation_cert", data={"keydata": cert})
        eq_(response.status_code, 400)

    def test_revocation_storage_with_malformed_cert_bad_rev_key_error(self):
        # Add an additional newline to the first newline of the cert
        # will trigger a CRC failure
        pos = REVOCATION_CERT2.find("\n")
        cert = REVOCATION_CERT2[:pos] + "\n" + REVOCATION_CERT2[pos:]
        response = self.client.put("/store_revocation_cert", data={"keydata": cert})
        eq_(response.status_code, 400)

    def test_revoke_cert_with_missing_arg(self):
        response = self.client.get("/revoke/?keyid={}".format(REVOCATION_ID))
        eq_(response.status_code, 400)

    def test_revoke_cert_when_no_request_made(self):
        response = self.client.get("/revoke/?keyid={}&token={}".format(REVOCATION_ID, TOKEN))
        eq_(response.status_code, 404)

    def test_request_revocation(self):
        response = self.perform_request_revocation()
        eq_(response.status_code, 200)
        eq_(response.data.decode("ascii"), "huzzah")

    def test_request_revocation_for_email_correctness(self):
        with patch("meg.email.Mail") as mock_mail:
            with patch("meg.api.uuid4") as mock_uuid:
                mock_uuid().hex = TOKEN
                response = self.perform_request_revocation()
                mock_mail().set_html.assert_called_with(EMAIL_HTML.format(
                    keyid=REVOCATION_ID,
                    link="http://localhost/revoke?keyid={}&token={}".format(
                        REVOCATION_ID, TOKEN
                    )
                ))

    def test_revoke_with_incorrect_token(self):
        self.perform_request_revocation()
        response = self.client.get("/revoke/?keyid={}&token={}".format(REVOCATION_ID, "blah"))
        eq_(response.status_code, 401)

    def test_revoke_success(self):
        self.perform_request_revocation()
        with patch("meg.api.addkey_to_sks") as mock_add:
            with patch("meg.stalks.GCM") as mock_gcm:
                mock_add.return_value = "", 200
                token_result = self.models.RevocationToken.query.filter(
                    self.models.RevocationToken.pgp_keyid_for == REVOCATION_ID
                ).one()
                self.perform_gcm_addition()
                response = self.client.get("/revoke/?keyid={}&token={}".format(
                    REVOCATION_ID, token_result.hex
                ))
                eq_(response.status_code, 200)

    def perform_gcm_addition(self):
        gcm_data = {
            "gcm_instance_id": GCM_IID, "phone_number": PHONE_NUMBER, "email": EMAIL1
        }
        response = self.client.put("/gcm_instance_id/", data=gcm_data)

    def perform_request_revocation(self):
        self.test_revocation_storage1()
        mock_content = {"key": "BLAH"}
        with patch("meg.api.get_key_by_id") as mock_requests:
            mock_requests.return_value = mock_content, 200
            with patch("meg.api.get_user_email_from_key") as mock_get_email:
                with patch("meg.email.SendGridClient") as mock_email_client:
                    mock_get_email.return_value = EMAIL1
                    mock_email_client().send.return_value = (200, "huzzah")
                    return self.client.post("/request_revoke/?keyid={}".format(REVOCATION_ID))
