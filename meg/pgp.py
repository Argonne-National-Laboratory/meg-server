"""
meg.pgp
~~~~~~~

Perform pgp related actions here
"""
from pgpdump import AsciiData
from pgpdump.packet import SignaturePacket
from sqlalchemy import and_

from meg.skier import make_get_request


def store_revocation_cert(db, armored_key, RevocationKey):
    ascii_data = AsciiData(armored_key.encode())
    packets = list(ascii_data.packets())

    # Temporary until we know if there is only 1 packet
    if len(packets) > 1:
        raise Exception("More than 1 packet")
    if len(packets) == 0:
        raise Exception("No packets found")

    signature = packets[0]
    if not isinstance(signature, SignaturePacket):
        raise Exception("No signature packet found")

    keyalgo = signature.hash_algorithm
    created = signature.creation_time
    expires = signature.expiration_time
    length = signature.length
    key_id = signature.key_id

    revocation_key = RevocationKey(keyalgo, created, expires, length, armored_key, key_id)
    db.session.add(revocation_key)
    db.session.commit()


def verify_trust_level(cfg, Signature, origin_keyid, contact_keyid):
    """
    Helper method for the API level task.

    0 if we directly trust contact
    1 if can be validated through web of trust
    2 if we cannot trust contact
    """
    if determine_if_implicitly_trusted(Signature, origin_keyid, contact_keyid):
        return 0
    elif determine_through_web_of_trust(cfg, Signature, origin_keyid, contact_keyid):
        return 1
    else:
        return 2


def determine_if_implicitly_trusted(Signature, origin_keyid, contact_keyid):
    """
    Determine if we directly trust the contact
    """
    results = Signature.query.filter(
        and_(Signature.pgp_keyid == origin_keyid, Signature.key_sfp_for == contact_keyid)
    )
    return True if results.first() else False


def determine_through_web_of_trust(cfg, Signature, origin_keyid, contact_keyid):
    """
    Find out if our contact is trusted through our web of trust

    This works by following a BFS search through contacts that we trust. It
    also cuts off at a max depth specified by the config. We don't want to
    crawl the entire DB each time a query goes off
    """
    def recursive_search(keyids, cur_depth):
        next_search = []
        for key in keyids:
            results = Signature.query.filter(Signature.pgp_keyid == key).all()
            for signature in results:
                if signature.key_sfp_for == contact_keyid:
                    return True
                elif signature.key_sfp_for != key:  # Don't bother looking at self signing
                    next_search.append(signature.key_sfp_for)

        cur_depth += 1
        if cur_depth > cfg.config.wot_bfs_max_depth:
            return False
        elif not next_search:  # If there are no more keys to look for
            return False

        for signature in results:
            recursive_search(next_search, cur_depth)

    cur_depth = 0
    return recursive_search([origin_keyid], cur_depth)
