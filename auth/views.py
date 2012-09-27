
import auth
from auth import forms as auth_forms

from google.appengine.ext.webapp import template

import webapp2
from webapp2_extras import auth as google_auth


class register(auth.UserAwareHandler):
    def get(self):
        self.render_response("templates/register.html", form=auth_forms.SignupForm())

    def post(self):
        form = auth_forms.SignupForm(self.request.POST)
        error = None
        if form.validate():
            success, info = self.auth.store.user_model.create_user(
                "auth:" + form.email.data,
                unique_properties=['email', 'username'],
                username = form.username.data,
                email= form.email.data,
                password_raw= form.password.data)

            if success:
                self.auth.get_user_by_password("auth:"+form.email.data,
                    form.password.data)
                return self.redirect_to("home")
            else:
                if user:
                    if 'email' in user:
                        error = "That email is already in use."
                else:
                    error = "Something has gone horibly wrong."

        else:
            import logging
            logging.warning(form.email)

        self.render_response("templates/register.html", form=form, error=error)


class login(auth.UserAwareHandler):
    def get(self):
        self.render_response("templates/login.html", form=auth_forms.LoginForm())

    def post(self):
        form = auth_forms.LoginForm(self.request.POST)
        error = None
        if form.validate():
            try:
                self.auth.get_user_by_password(
                    "auth:"+form.email.data,
                    form.password.data)
                return self.redirect('/')
            except (google_auth.InvalidAuthIdError, google_auth.InvalidPasswordError):
                error = "Invalid Email / Password"

        self.render_response("templates/login.html",
            form=form,
            error=error)


class logout(auth.UserAwareHandler):
    """Destroy the user session and return them to the login screen."""
    @auth.login_required
    def get(self):
        self.auth.unset_session()
        self.redirect('/auth/login')