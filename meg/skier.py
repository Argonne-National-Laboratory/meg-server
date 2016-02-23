"""
meg.skier
~~~~~~~~~

Helper functions we can use for interacting with skier
"""
import requests


def make_get_request(cfg, api, arg):
    urn = "{}/{}".format(server_url,  api, arg)
    return make_skier_request(cfg, requests.get, urn)


def make_skier_request(cfg, func, urn):
    """
    Get skier specific info. Just act as a thin proxy.
    """
    keyservers = cfg.config.keyservers
    for server_url in keyservers:
        r = func("{}/api/v1/{}".format(server_url, urn))
        if r.status_code != 200:
            continue
        return r.content, 200
    else:
        return r.content, r.status_code
