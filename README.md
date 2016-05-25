# meg-server
Server side actions for MEG.

## Installation
Installation can be done using ansible. Since megserver is built with python3 but
ansible does not support python3 you must create a new virtualenv for python2 and
install ansible

    virtualenv venv27
    source venv27/bin/activate
    pip install ansible

Then you can install meg on your server. If need be modify ansible/inventory so
that your inventory file can point to the server you wish to install on. After this
is completed then you can deploy the server

    cd ansible
    ansible-playbook -i inventory deploy.yml --extra-vars 'meg_user_password=<meg db pw> skier_user_password=<skier db pw> megserver_gcm_api_key=<gcm api key> sendgrid_api_key=<sendgrid api secret>'

If you just want to upgrade your version of megserver/skier then you can use a tag

    ansible-playbook -i inventory deploy.yml --extra-vars 'meg_user_password=<meg db pw> skier_user_password=<skier db pw> megserver_gcm_api_key=<gcm api key> sendgrid_api_key=<sendgrid api secret>' -t <skier OR megserver>

## API
megserver provides a wrapper around PGP keyserver APIs and adds additional APIs for
MEG specific functionality as well.

### addkey
Add an armored PGP public key.

    PUT addkey

    body:
    keydata=<armored PGP public key>

### getkey
Get a key by an 8 char key id

    GET /getkey/<keyid>


### get_trust_level
Get the trust level of a contacting key.

    GET /get_trust_level/<message origin key id>/<recipient key id>

Returns:

 * `0` if we origin directly trusts the contact
 * `1` if origin trusts contact through web of trust
 * `2` if origin does not trust contact

### store_revocation_cert
Store a revocation certificate on the server

    PUT /store_revocation_cert/

    body:
    keydata=<revocation certificate>

### request_revoke
Request that a users public key be revoked

    POST /request_revoke/?keyid=<8 digit public key id>

### revoke
Revoke a users public key

    GET /revoke/?keyid=<8 digit public key id>&token=<revocation token>

### search
Search for a users public key by some string, maybe by email address or name

    GET /search/<search string>

### getkey_by_message_id
Get a users public key of the user we want to send a message to by the id of a
message awaiting pick up from the server. This API is only called by the phone
when it wants to encrypt a message.

    GET /getkey_by_message_id/?associated_message_id=<message id>

note: This API should probably go away in the future for simplicity sake

### decrypted_message
Get a message (that is encrypted by AES symmetric key) that is PGP decrypted. There are two cases here.

1. Get a message by message id. This is used by the phone

    GET /decrypted_message/?message_id=<message id>

2. Get a message by to and from email address

    GET /decrypted_message/?email\_to=<recipient email address>&email\_from=<origin email address>

Put a PGP decrypted email on the server. The message must be base64 encoded.

    PUT /decrypted_message/?action=<action>&email_to=<recipient address>&email_from=<origin address>
    Content-Type: text/plain

    data:
    <base64 encoded message>

#### actions
The list of actions available for this API are

 * toclient
 * encrypt
 * decrypt

### encrypted_message
Get a message that is PGP encrypted from the server. The methods here are almost the exact same as the actions that we can perform for a PGP decrypted message. In fact it would probably just be easier to consolidate this API with the `decrypted_message` one and just name the API `message`.

1. Get a message by message id. This is used by the phone

    GET /encrypted_message/?message_id=<message id>

2. Get a message by to and from email address

    GET /encrypted_message/?email\_to=<recipient email address>&email\_from=<origin email address>

Put a PGP encrypted email on the server. The message must be base64 encoded

    PUT /encrypted_message/?action=<action>&email_to=<recipient address>&email_from=<origin address>
    Content-Type: text/plain

    data:
    <base 64 encoded message>

## Acknowledgements
To SunDwarf's work done on Skier that serves as a basis and inspiration for
the code in this repo
