"""
meg.sks
~~~~~~~

Helper functions we can use for interacting with sks
"""
import json
import re

from bs4 import BeautifulSoup
import requests

from meg.constants import HTML_PARSER


def get_all_key_signatures(cfg, keyid):
    """
    Get all signatures for a specific key. We exclude self signed signatures
    because this is not helpful for us.
    """
    content, status_code = make_sks_request(
        cfg, requests.get, "lookup", {"op": "vindex", "search": "0x{}".format(keyid)}, None
    )
    if status_code != 200:
        return status_code, content
    elem = BeautifulSoup(content, HTML_PARSER).span
    ids = []
    while (elem.findNext().name != "strong" and elem.findNext()):
        elem = elem.findNext()
        if "op=get" in elem["href"] and elem.text != keyid:
            ids.append(elem.text)
    return ids


def make_sks_request(cfg, func, urn, params, data):
    """
    Get sks specific info. Just act as a thin proxy.
    """
    keyservers = cfg.config.keyservers
    for server_url in keyservers:
        r = func("{}/{}".format(server_url, urn), params=params, data=data)
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
        cfg, requests.get, "lookup", {"op": "index", "search": search_str}, None
    )
    if status_code != 200:
        return content, status_code
    bs = BeautifulSoup(content, HTML_PARSER)
    regex = re.compile(r"^pub *\d{3,4}\w\/([\w\d]{8})")
    ids = []
    for pre in bs.findAll("pre"):
        match = regex.search(pre.text.strip("\r\n"))
        if match and not "KEY REVOKED" in pre.text:
            ids.append(match.groups()[0])
    return {"ids": ids}, status_code


def get_key_by_id(cfg, keyid):
    """
    Get the PGP public key by a given id
    """
    content, status_code = make_sks_request(
        cfg, requests.get, "lookup", {"op": "get", "search": "0x{}".format(keyid)}, None
    )
    if status_code != 200:
        return content, status_code
    return {"key": BeautifulSoup(content, HTML_PARSER).pre.text.strip("\r\n")}, status_code


def addkey_to_sks(cfg, keytext):
    """
    Add a key to SKS
    """
    return make_sks_request(cfg, requests.post, "add", None, {"keytext": keytext})
