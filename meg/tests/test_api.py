import os
from unittest.mock import patch

from flask import Flask
from flask.ext.testing import TestCase
from nose.tools import eq_

from meg.app import create_app as make_app


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

class MockResponse(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json():
        # Hopefully we provided our content as a dictionary
        return content


class TestMEGAPI(TestCase):
    def create_app(self):
        app, self.db = make_app(debug=True, testing=True)
        return app

    def setUp(self):
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_revocation_storage(self):
        """
        This test is not a guarantee that the DB interactions will work
        correctly but at least validates that something on the code
        side of things is not horribly wrong
        """
        response = self.client.put("/store_revocation_cert", data={"keydata": REVOCATION_CERT})
        eq_(response.status_code, 200)

    def test_addkey(self):
        mock_content = "blah"
        with patch("meg.api.requests") as mock_requests:
            mock_requests.put.return_value = MockResponse(200, mock_content)
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
            "http://ithilien:5000/api/v1/keyinfo/1111B": MockResponse(
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
            "http://ithilien:5000/api/v1/keyinfo/1111B": MockResponse(
                200, '{"sigs": {"1111B": [["1111B"], ["1111C"]]}}'
            ),
            "http://ithilien:5000/api/v1/keyinfo/1111C": MockResponse(
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
        self.test_revocation_storage()
        mock_content = "blah"
        with patch("meg.api.requests") as mock_requests:
            mock_requests.post.return_value = MockResponse(200, mock_content)
            response = self.client.post("/revoke_certificate/{}".format(REVOCATION_ID))
            eq_(response.status_code, 200)
            eq_(response.data.decode(), mock_content)

    def test_revoke_cert_with_no_key(self):
        response = self.client.post("/revoke_certificate/11111A")
        eq_(response.status_code, 404)
