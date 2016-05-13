"""
meg.email
~~~~~~~~~

Performs email functions for MEG
"""
import os
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

import requests
from sendgrid import Mail, SendGridClient

from meg.constants import EMAIL_HTML
from meg.pgp import get_pgp_key_data, get_user_id_packet


def send_revocation_request_email(cfg, keyid, hex, user_email):
    client = SendGridClient(cfg.config.sendgrid.api_key)
    message = get_sendgrid_request_message(cfg, keyid, hex, user_email)
    response = client.send(message)
    # return content, code
    return response[1], response[0]


def get_sendgrid_request_message(cfg, keyid, hex, user_email):
    url_prefix = urljoin(
        cfg.config.megserver_hostname_url,
        os.path.join(cfg.config.meg_url_prefix, "revoke")
    )
    params = urlencode([("keyid", keyid), ("token", hex)])
    parsed = list(urlparse(url_prefix))
    parsed[4] = params
    revocation_link = urlunparse(parsed)

    message = Mail()
    message.add_to(user_email)
    message.set_from(cfg.config.sendgrid.from_email)
    message.set_subject(cfg.config.sendgrid.subject)
    message.set_html(EMAIL_HTML.format(keyid=keyid, link=revocation_link))
    return message
