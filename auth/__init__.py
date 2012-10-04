import os

import webapp2
from webapp2_extras import sessions
from webapp2_extras import auth as webapp_auth
from google.appengine.ext.webapp import template

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
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="datastore")

    def dispatch(self):
        try:
            super(UserAwareHandler, self).dispatch()
        finally:
            # Save the session after each request
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return webapp_auth.get_auth(request=self.request)

    @webapp2.cached_property
    def user(self):
        user = self.auth.get_user_by_session()
        return user

    @webapp2.cached_property
    def user_model(self):
        user_model, timestamp = self.auth.store.user_model.get_by_auth_token(
            self.user['user_id'],
            self.user['token']) if self.user else (None, None)

        import logging
#        logging.warning(user_model.username)
        return user_model

    def render_response(self, temp, view_context={}, form=None, error=None):
        context = {}
        #put stuff in context here like base.get_context would normally have.

        ##
        context.update(view_context)

        if 'form' not in context:
            context['form'] = form

        self.response.out.write(template.render(temp, context))