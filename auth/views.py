import json

import auth
from auth import forms as auth_forms
from auth import utils as auth_utils
from auth import models as auth_models

from flask import redirect
from flask import request
from flask.templating import render_template

from libs import flask_login


class register(auth.UserAwareView):
    def get(self):
        return render_template("register.html", form=auth_forms.SignupForm())

    def post(self):
        form = auth_forms.SignupForm(request.form)
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

        return render_template("register.html", form=form, error=error)


class login(auth.UserAwareView):
    def get(self):
        return render_template("login.html", form=auth_forms.LoginForm())

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
                flask_login.login_user(auth_models.WTUser.all().filter('email =', form.email.data).fetch(1)[0])

        response = json.dumps({'loggedin': loggedin, 'error_message': message})
        return response


class logout(auth.UserAwareView):
    @auth.login_required
    def get(self):
        flask_login.logout_user()
        return redirect('/auth/login')


class check_username(auth.UserAwareView):
    def get(self):
        username = self.request.GET.get('username', None)

        output = {"valid" : True}
        count = auth_models.WTUser.all().filter('username =', username).count()

        if count > 0:
            output['valid'] = False

        return json.dumps(output)

