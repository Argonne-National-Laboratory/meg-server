"""
Test the celery workers we are using
"""
import os
from unittest.mock import Mock, patch

from celery import Celery
from configmaster.YAMLConfigFile import YAMLConfigFile
from nose.tools import eq_

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
            tasks.transmit_gcm_id("foobar", 1)
            mock_gcm.assert_called_with(self.cfg.config.gcm_api_key)
            print(mock_gcm.call_args_list)
            # ensure we didnt retry. We called it earlier in the test
            eq_(mock_gcm.call_count, 2)

    def test_transmit_gcm_id_with_error(self):
        with patch("meg.stalks.GCM") as mock_gcm:
            mock_gcm().json_request.return_value = "errors 500!"
            tasks = create_celery_routes(self.celery, self.cfg)
            retry_mocker = Mock()
            tasks.transmit_gcm_id.retry = retry_mocker
            tasks.transmit_gcm_id("foobar", 1)
            retry_mocker.assert_called_once_with(
                args=["foobar", 1], countdown=self.cfg.config.celery.transmit_gcm_id.timeout
            )
