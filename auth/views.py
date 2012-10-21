import json
import logging

import auth
from auth import forms as auth_forms
from auth import utils as auth_utils
from auth import models as auth_models

from flask import redirect
from flask import request
from flask.templating import render_template

from lib import flask_login


class register(auth.UserAwareView):
    def get(self):
        return render_template("auth/register.html", form=auth_forms.SignupForm())

    def post(self):
        form = auth_forms.SignupForm(request.form)
        message = None
        registered = False
        if form.validate():
            password, salt = auth_utils.encode_password(form.password.data)

            current_user = auth_models.WTUser.all().filter('email', form.email.data).count()

            if not current_user:
                new_user = auth_models.WTUser(username=form.username.data,
                                              email=form.email.data,
                                              password=password,
                                              salt=salt)
                new_user.save()

                if new_user:
                    registered = True
                    auth_utils.send_registration_email(form.email.data, form.username.data)
                    flask_login.login_user(auth_models.WTUser.all().filter('email =', form.email.data).fetch(1)[0])

            if current_user:
                message = "Whoops! An account has already been registered with that email."

        if form.errors:
            message = form.errors

        response = json.dumps({'registered': registered, 'error_message': message})
        return response


class login(auth.UserAwareView):
    def get(self):
        return render_template("auth/login.html", form=auth_forms.LoginForm())

    def post(self):

        form = auth_forms.LoginForm(request.form)
        error = None
        loggedin = False
        message = None

        if form.validate():

            loggedin = auth_utils.check_password(form.password.data, form.email.data)

            if not loggedin:
                message = "Invalid Email / Password"
            else:
                flask_login.login_user(auth_models.WTUser.all().filter('email =', form.email.data).fetch(1)[0],
                                       remember=form.remember_me.data)

        next_url = '/tournament/list'
        response = json.dumps({'loggedin': loggedin, 'error_message': message, 'next_url': next_url})
        return response


class logout(auth.UserAwareView):
    @auth.login_required
    def get(self):
        flask_login.logout_user()
        return redirect('/auth/login')


class check_username(auth.UserAwareView):
    def get(self):
        username = request.args.get('username', None)

        output = {"valid" : True}
        count = auth_models.WTUser.all().filter('username =', username).count()

        if count > 0:
            output['valid'] = False

        return json.dumps(output)

class welcome(auth.UserAwareView):
    def get(self):
        return render_template('auth/welcome.html')

