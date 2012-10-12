from flask.views import MethodView
from flask import session, redirect, url_for

#import lib.gaesessions
#from lib.gaesessions import get_current_session

from auth import models as auth_models


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
    def auth(self):
        return #webapp_auth.get_auth(request=self.request)

    @property
    def user(self):
        if 'user' in self.session:
            return self.session['user']

#    def render_response(self, temp, view_context={}, form=None, error=None):
#        context = {}
#        #put stuff in context here like base.get_context would normally have.
#
#        ##
#        context.update(view_context)
#
#        if 'form' not in context:
#            context['form'] = form
#
#        self.response.out.write(self.jinja2.render_template(temp, **context))