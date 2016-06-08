"""
meg.skier
~~~~~~~~~

Helper functions we can use for interacting with skier
"""
import json

from bs4 import BeautifulSoup
import requests


def get_all_key_signatures(cfg, keyid):
    """
    Get all signatures for a specific key

	The JSON response looks like

	We exclude subkeys from the signing because this doesn't
	contribute to WoT. Neither does self signing.
    """
    content, status_code = make_sks_request(
        cfg, requests.get, "lookup", {"op": "vindex", "search": "0x{}".format(keyid)}
    )
    if status_code != 200:
        return status_code, content
    elem = BeautifulSoup(content).span
    ids = []
    while (elem.findNext().name != "strong" and elem.findNext()):
        elem = elem.findNext()
        if "op=get" in elem["href"] and elem.text != keyid:
            ids.append(keyid)
    return ids


def make_sks_request(cfg, func, urn, params):
    """
    Get sks specific info. Just act as a thin proxy.
    """
    keyservers = cfg.config.keyservers
    for server_url in keyservers:
        r = func("{}/{}".format(server_url, urn), params=params)
        if r.status_code != 200:
            continue
        return r.content, 200
    else:
        return r.content, r.status_code


def search_key(cfg, search_str):
    """
    Search for a key by a given string
    """
    content, status_code = make_sks_request(
        cfg, requests.get, "lookup", {"op": "index", "search": search_str}
    )
    if status_code != 200:
        return content, status_code
    bs = BeautifulSoup(content)
    ids = [a.text for a in bs.findAll("a") if "op=get" in a["href"]]
    return {"ids": ids}


def get_key_by_id(cfg, keyid):
    """
    Get the PGP public key by a given id
    """
    content, status_code = make_sks_request(
        cfg, requests.get, "lookup", {"op": "get", "search": "0x{}".format(keyid)}
    )
    if status_code != 200:
        return content, status_code
    return {"key": BeautifulSoup(content).pre.text}, status_code


def addkey_to_sks(cfg, keytext):
    """
    Add a key to SKS
    """
    return make_sks_request(cfg, requests.post, "add", {"keytext": keytext})
