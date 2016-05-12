"""
meg.email
~~~~~~~~~

Performs email functions for MEG
"""
import requests
from sendgrid import Mail, SendGridClient

from meg.pgp import get_pgp_key_data, get_user_id_packet


def send_revocation_request_email(cfg, key_id, hex, user_email):
    client = SendGridClient(cfg.config.sendgrid.api_key)
    message = get_sendgrid_request_message(cfg, key_id, hex, user_email)
    response = client.send(message)
    # return content, code
    return response[1], response[0]


def get_sendgrid_request_message(cfg, key_id, hex, user_email):
    html = """
    <div>We have received a request that the GPG key with id:&nbsp;{key_id}&nbsp;be revoked. If this is correct then click the link below. This link will not be valid after an hour</div>

    <div>&nbsp;</div>

    <div>{link}</div>
    """
    revocation_link = "{}/{}/?key_id={}&token={}".format(
        cfg.config.megserver_hostname_url,
        cfg.config.meg_url_prefix,
        key_id,
        hex
    )
    message = Mail()
    message.add_to(user_email)
    message.set_from(cfg.config.sendgrid.from_email)
    message.set_subject(cfg.config.sendgrid.subject)
    message.set_html(html.format(key_id=key_id, link=revocation_link))
    return message
