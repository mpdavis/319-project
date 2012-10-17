
from auth import models as auth_models

from flask.views import MethodView

from flask import session
from flask import redirect
from flask import url_for

from libs import flask_login

import settings


def login_required(handler):
    "Requires that a user be logged in to access the resource"
    def check_login(self, *args, **kwargs):
        if not self.user:
            return redirect(url_for('login'))
        else:
            return handler(self, *args, **kwargs)
    return check_login


class UserAwareView(MethodView):

    @property
    def session(self):
        return session

    @property
    def user(self):
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user
        else:
            return None

    def get_context(self):
        ctx = {
            'MEDIA_MERGED': settings.MEDIA_MERGED,
        }
        return ctx
