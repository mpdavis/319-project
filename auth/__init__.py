import os

import webapp2
from webapp2_extras import sessions
from webapp2_extras import auth as webapp_auth
from google.appengine.ext.webapp import template

import lib.gaesessions

from lib.gaesessions import get_current_session

from auth import models as auth_models

def login_required(handler):
    "Requires that a user be logged in to access the resource"
    def check_login(self, *args, **kwargs):
        if not self.user:
            return self.redirect_to('login')
        else:
            return handler(self, *args, **kwargs)
    return check_login

class UserAwareHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def session(self):
        return get_current_session()

    @webapp2.cached_property
    def auth(self):
        return webapp_auth.get_auth(request=self.request)

    @webapp2.cached_property
    def user(self):
        if 'user' in self.session:
            return self.session['user']

    def render_response(self, temp, view_context={}, form=None, error=None):
        context = {}
        #put stuff in context here like base.get_context would normally have.

        ##
        context.update(view_context)

        if 'form' not in context:
            context['form'] = form

        self.response.out.write(template.render(temp, context))