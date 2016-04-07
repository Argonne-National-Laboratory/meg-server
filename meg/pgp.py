"""
meg.pgp
~~~~~~~

Perform pgp related actions here
"""
from pgpdump import AsciiData
from pgpdump.packet import SignaturePacket
from pgpdump.utils import PgpdumpException
from sqlalchemy import and_

from meg.exception import BadRevocationKeyException
from meg.skier import get_all_key_signatures, make_get_request


def store_revocation_cert(db, armored_key, RevocationKey):
    # First be able to ensure we can add an extra newline on the fly.
    try:
        ascii_data = AsciiData(armored_key.encode())
    except PgpdumpException as err:
        # It's all bouncy castles fault. we need to insert an additional newline
        if "BCPG" in armored_key:
            position = armored_key.find("BCPG")
            newline = armored_key.find("\n", position)
            new_armored_key = armored_key[0:newline] + "\n" + armored_key[newline:]
            ascii_data = AsciiData(new_armored_key.encode())
        else:
            raise err

    packets = list(ascii_data.packets())

    if len(packets) == 0:
        raise BadRevocationKeyException("No packets found")

    for packet in packets:
        if isinstance(packet, SignaturePacket):
            if packet.sig_type == "Key revocation signature":
                signature = packet
                break
    else:
        raise BadRevocationKeyException("No signature packet found")

    signature = packets[0]

    created = signature.creation_time
    expires = signature.expiration_time
    length = signature.length
    key_id = signature.key_id.decode()[-8:]  # We just need the last 8 chars

    revocation_key = RevocationKey(created, expires, length, armored_key, key_id)
    db.session.add(revocation_key)
    db.session.commit()


def verify_trust_level(cfg, origin_keyid, contact_keyid):
    """
    Helper method for the API level task.

    0 if we directly trust contact
    1 if can be validated through web of trust
    2 if we cannot trust contact
    """
    if determine_if_explicitly_trusted(cfg, origin_keyid, contact_keyid):
        return 0
    elif determine_through_web_of_trust(cfg, origin_keyid, contact_keyid):
        return 1
    else:
        return 2


def determine_if_explicitly_trusted(cfg, origin_keyid, contact_keyid):
    """
    Determine if we directly trust the contact
    """
    results = get_all_key_signatures(cfg, contact_keyid)
    if not isinstance(results, list):  # Is a tuple of (status_code, content)
        return False
    return True if origin_keyid in results else False


def determine_through_web_of_trust(cfg, origin_keyid, contact_keyid):
    """
    Find out if our contact is trusted through our web of trust

    This works by following a BFS search through contacts that we trust. It
    also cuts off at a max depth specified by the config. We don't want to
    crawl the entire DB each time a query goes off
    """
    def recursive_search(keyids, cur_depth):
        next_search = []
        for key in keyids:
            results = get_all_key_signatures(cfg, key)
            # If there was an error on the keyserver side
            if not isinstance(results, list):
                continue
            for signature in results:
                if signature == origin_keyid:
                    return True
                next_search.append(signature)

        cur_depth += 1
        if cur_depth > cfg.config.wot_bfs_max_depth:
            return False
        elif not next_search:  # If there are no more keys to look for
            return False

        for signature in results:
            return recursive_search(next_search, cur_depth)

    cur_depth = 0
    return recursive_search([contact_keyid], cur_depth)
