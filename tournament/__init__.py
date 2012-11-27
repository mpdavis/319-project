from flask import request, redirect, url_for, g, abort
from functools import wraps

from tournament import actions
from tournament import models


def public_tournament(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = kwargs.get('tournament_key')
        tournament = actions.get_tournament_by_key(key)
        if tournament and tournament.perms == models.Tournament.PUBLIC:
            return f(*args, **kwargs)
        return abort(404)
    return decorated_function