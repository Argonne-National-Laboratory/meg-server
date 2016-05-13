PHONE_ACTIONS = ["encrypt", "decrypt"]
APPROVED_ACTIONS = PHONE_ACTIONS + ["toclient"]
EMAIL_HTML = """
<div>We have received a request that the GPG key with id:&nbsp;{keyid}&nbsp;be revoked. If this is correct then click the link below. This link will not be valid after an hour</div>

<div>&nbsp;</div>

<div>{link}</div>
"""
