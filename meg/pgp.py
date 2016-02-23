"""
meg.pgp
~~~~~~~

Perform pgp related actions here
"""
from pgpdump import AsciiData
from pgpdump.packet import SignaturePacket


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
