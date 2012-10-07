
import json
import logging

import auth
from auth import forms as auth_forms
from auth import utils as auth_utils
from auth import models as auth_models

from google.appengine.ext.webapp import template
from google.appengine.ext import db

import webapp2
from webapp2_extras import auth as google_auth


class register(auth.UserAwareHandler):
    def get(self):
        self.render_response("templates/register.html", form=auth_forms.SignupForm())

    def post(self):
        form = auth_forms.SignupForm(self.request.POST)
        error = None
        if form.validate():
            password, salt = auth_utils.encode_password(form.password.data)

            new_user = auth_models.WTUser(username=form.username.data,
                                          email=form.email.data,
                                          password=password,
                                          salt=salt)
            new_user.save()

            if new_user:
                auth_utils.send_registration_email(form.email.data, form.username.data)

            else:
                if user:
                    if 'email' in user:
                        error = "That email is already in use."
                else:
                    error = "Something has gone horibly wrong."

        self.render_response("templates/register.html", form=form, error=error)


class login(auth.UserAwareHandler):
    def get(self):
        self.render_response("templates/login.html", form=auth_forms.LoginForm())

    def post(self):

        form = auth_forms.LoginForm(self.request.POST)
        error = None
        loggedin = False
        message = None

        if form.validate():
            loggedin = auth_utils.check_password(form.password.data, form.email.data)

            if not loggedin:
                message = "Invalid Email / Password"
            else:
                self.session['user'] = auth_models.WTUser.all().filter('email =', form.email.data).fetch(1)[0]

        response = json.dumps({'loggedin': loggedin, 'error_message': message})

        self.response.write(response)


class logout(auth.UserAwareHandler):
    """Destroy the user session and return them to the login screen."""
    @auth.login_required
    def get(self):
        if self.session.is_active():
            self.session.terminate()

        self.redirect('/auth/login')

class check_username(auth.UserAwareHandler):
    def get(self):
        username = self.request.GET.get('username', None)

        output = {"valid" : True}
        count = auth_models.WTUser.all().filter('username =', username).count()

        if count > 0:
            output['valid'] = False

        self.response.write(json.dumps(output))

