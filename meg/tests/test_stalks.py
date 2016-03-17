"""
Test the celery workers we are using
"""
import os
from unittest.mock import Mock, patch

from celery import Celery
from configmaster.YAMLConfigFile import YAMLConfigFile
from nose.tools import assert_raises, eq_

from meg.stalks import create_celery_routes


class TestStalks(object):
    def setup(self):
        self.celery = Celery()
        dirname = os.path.dirname(__file__)
        self.cfg = YAMLConfigFile(os.path.join(dirname, "../config.default.yml"))

    def test_transmit_gcm_id(self):
        with patch("meg.stalks.GCM") as mock_gcm:
            mock_gcm().json_request.return_value = "Success!"
            tasks = create_celery_routes(self.celery, self.cfg)
            tasks.transmit_gcm_id("foobar", 1, "encrypt")
            mock_gcm.assert_called_with(self.cfg.config.gcm_api_key)
            mock_gcm.json_request(registration_ids=["foobar"], data={"message_id": 1, "action": "encrypt"})
            eq_(mock_gcm.call_count, 2)

    def test_transmit_gcm_id_with_bad_action(self):
        tasks = create_celery_routes(self.celery, self.cfg)
        assert_raises(Exception, tasks.transmit_gcm_id, "foobar", 1, "baz!")

    def test_transmit_gcm_id_with_error(self):
        with patch("meg.stalks.GCM") as mock_gcm:
            mock_gcm().json_request.return_value = "errors 500!"
            tasks = create_celery_routes(self.celery, self.cfg)
            retry_mocker = Mock()
            tasks.transmit_gcm_id.retry = retry_mocker
            tasks.transmit_gcm_id("foobar", 1, "decrypt")
            retry_mocker.assert_called_once_with(
                args=["foobar", 1, "decrypt"], countdown=self.cfg.config.celery.transmit_gcm_id.timeout
            )
