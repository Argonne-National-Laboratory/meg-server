"""
meg.skier
~~~~~~~~~

Helper functions we can use for interacting with skier
"""
import json

import requests


def get_all_key_signatures(cfg, keyid):
    """
    Get all signatures for a specific key

	The JSON response looks like

	 u'sigs': {u'<master key>': [[u'<master key>',
		[{u'comment': None,
		  ...
		19],
	   [u'<first signing key>',
		[{u'comment': None,
          ...
		16]],
	  u'<subkey 1>': [[u'<master key>',
		[{u'comment': None,
          ...
		24]]},

	We exclude subkeys from the signing because this doesn't
	contribute to WoT. Neither does self signing. So we exclude this
    as well
    """
    content, status_code = make_get_request(cfg, "keyinfo", keyid)
    if status_code != 200:
        return status_code, content
    sigs_list = json.loads(content)["sigs"][keyid]
    return list(filter(lambda newsig: newsig,
        map(lambda sig: sig[0] if sig[0] != keyid else None, sigs_list)
    ))


def make_get_request(cfg, api, arg):
    urn = "{}/{}".format(api, arg)
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
