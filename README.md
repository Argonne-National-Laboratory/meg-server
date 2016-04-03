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
    ansible-playbook -i inventory deploy.yml --extra-vars 'meg_user_password=<meg db pw> skier_user_password=<skier db pw>'

If you just want to upgrade your version of megserver/skier then you can use a tag

    ansible-playbook -i inventory deploy.yml --extra-vars 'meg_user_password=<meg db pw> skier_user_password=<skier db pw>' -t <skier OR megserver>

## API
megserver provides a wrapper around PGP keyserver APIs and adds additional APIs for
MEG specific functionality as well.

TODO

## Acknowledgements
To SunDwarf's work done on Skier that serves as a basis and inspiration for
the code in this repo
