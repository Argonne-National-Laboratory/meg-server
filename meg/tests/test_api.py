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

iQElBCABCAAPBQJWy706CB0AZm9vYmFyAAoJEOeC9ljK6Z2cYFQH/1o7l8Zz+LVH
YT8txGwVLnN84rxEAAjMcoiOrsHkKKGCxu6qcK6Zt5RvgpLN9pr283P2WaTRxagX
qeD0DC2I+TNNEpn/tHILcpV0Q9CtgY30Hvyzfm1pd9HwKobB8nxt2pVJGlEfhTZy
ssMb8seIsAl5Ccws6XQn540Ua+KTnKesKLo6P6KoBfLG36mUF0sViQyuOms4NBFg
N964TRBCFixaaUUf5nnlT1PQcW1+bvFvrIMjVeuxeDzOCfaPxZjhavieWMQDvmgy
PVCiOvA+YdWNojLWKiwaocWrsrn0tW9fJ0ugk2Wz/sIfo08Z7tKSnbirF2Otg6UL
KtJtLoGaduI=
=qITv
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
