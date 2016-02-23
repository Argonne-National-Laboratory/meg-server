import os

from flask import Flask
from flask.ext.testing import TestCase
from nose.tools import eq_

from meg.api import create_routes
from meg.cfg import configure_app
from meg.db import create_db, generate_models


REVOCATION_CERT = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2
Comment: A revocation certificate should follow

iQIfBCABCAAJBQJWyYUbAh0AAAoJEIr8UVUcfyMQQUMP/RisyG6iKwovKJz6Wt1Y
m0a8iD9uoNo7rEtH+OEu1dbFUvHLNXA1KWRKFhmbCqidsYIGLtTqf68gPQE/f9eL
9uW1J1WVQSJaSmOdHVYm+x3BDwml+Jai++nSJeRXPvdcWcqtXsvjR1Gb9gEwMNpz
cYXo7UJ80ei1pYWBtgBA416i/bBqMQBPCrdxCRO6aZz5U+sb8+TqNh89+6mCwgkA
Rxiy5Ir7qPh1jHCqMkOlb7wlFbwmzj+zKezUH6cHK8M4U0LjiwkBIBHpSsmxaYau
Bkte6+4LLB8w/WiruVcqkxK9VoV1tNrFyM8pZB3PZmIVhDEElUPfu7SaEUOrPdnn
3jlGF5304p7EMGip37z+H2z9weaaekVk6G2ffXOH96OD8BjmhyCqgO/j8zDkiOnl
WfsFJv0j6NEf0RCKm0qOP0VVVYTiTYVPczsjQ9JiauMvukrOmf5BUIRXCZ8c05Dz
Gmv7HlzNOfodgTpGqDyvmLYfOCeIkc2MOTQVlph5LXcXmPaUVCNLHtzKMEa6wIPJ
N7exHVUysCWfS0qgUVmK6y02F49Z29KIM7BguPcmJSlsKLJceBKT95jXWIp77BAQ
JOSXgjKSN+A+uHb496fjtmFZ4xSQcR230IFyLDMqbkMoPL2BMSvSPUWkee8BTSzF
5/BP1JfxK3M2XPqLivNAy0S6
=A1Jv
-----END PGP PUBLIC KEY BLOCK-----"""

class TestMEGAPI(TestCase):
    def create_app(self):
        app = Flask(__name__)
        cfg = configure_app(app, testing=True, debug=True)
        self.db = create_db(app)
        r, _ = generate_models(self.db)
        create_routes(app, self.db, cfg, r)
        return app

    def setUp(self):
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_revocation_storage(self):
        response = self.client.put("/store_revocation_cert", data={"keydata": REVOCATION_CERT})
        eq_(response.status_code, 200)
