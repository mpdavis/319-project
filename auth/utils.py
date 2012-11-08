import hashlib
import logging
import string
import random

from auth import models as auth_models

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits


def generate_salt(size=64):
    random.seed()
    return ''.join([random.choice(ALPHABET) for i in range(0, size)])


def encode_password(raw_password, salt=None):

    if not salt:
        salt = generate_salt()

    h = hashlib.new('sha512')
    h.update(raw_password)
    h.update(salt)

    return h.hexdigest(), salt

def check_password(raw_password, email):
    user = auth_models.WTUser.all().filter('email =', email).fetch(1)

    if len(user):
        user = user[0]
        response_hash, salt = encode_password(raw_password, user.salt)
        return response_hash == user.password

    else:
        return False
