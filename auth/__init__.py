import auth
from auth import models as auth_models

from flask import session, redirect, url_for
from flask.views import MethodView

from lib import flask_login
from lib.flask_login import LoginManager

import settings


def initialize(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.unauthorized_handler(user_unauthorized_callback)
    login_manager.user_loader(load_user)


def user_unauthorized_callback():
    return redirect(url_for('login'))


def load_user(userid):
    return auth_models.WTUser.get_by_id(int(userid))


class UserAwareView(MethodView):
    active_nav = None

    @property
    def session(self):
        return session

    @property
    def user(self):
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user._get_current_object()
        else:
            return None

    def get_context(self, extra_ctx=None, **kwargs):
        ctx = {
            'MEDIA_MERGED': settings.MEDIA_MERGED,
            'user': self.user,
            'active_nav': self.active_nav,
        }
        if extra_ctx:
            ctx.update(extra_ctx)
        ctx.update(kwargs)
        return ctx
