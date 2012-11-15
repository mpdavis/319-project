import json

import auth
from auth import forms as auth_forms
from auth import utils as auth_utils
from auth import models as auth_models

from base import mail

from flask import url_for
from flask import redirect
from flask import request
from flask import session
from flask.templating import render_template

from lib import flask_login
from lib.flask_login import login_required

from lib import flask_oauth
from lib.flask_oauth import OAuth

import settings

oauth = OAuth()

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=settings.FACEBOOK_APP_ID,
                            consumer_secret=settings.FACEBOOK_APP_SECRET,
                            request_token_params={'scope': 'email'}
)

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=settings.GOOGLE_CLIENT_ID,
                          consumer_secret=settings.GOOGLE_SECRET)


class Register(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        context['form'] = auth_forms.SignupForm()
        return render_template("auth/register.html", **context)

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

                    subject = "Welcome to Web Tournaments"
                    body = mail.generate_email_body("email/auth/registration_email.txt", username=new_user.username)

                    mail.send_email(new_user.email, subject, body)

                    flask_login.login_user(new_user)

            if current_user:
                message = "Whoops! An account has already been registered with that email."

        if form.errors:
            message = form.errors

        response = json.dumps({'registered': registered, 'error_message': message})
        return response


class Login(auth.UserAwareView):
    def get(self):
        context = self.get_context(form = auth_forms.LoginForm())
        return render_template("auth/login.html", **context)

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

class FacebookLogin(auth.UserAwareView):

    def get(self):
         return facebook.authorize(callback=url_for('facebook_authorized',
                                                   next=request.args.get('next') or request.referrer or None,
                                                   _external=True))

class GoogleLogin(auth.UserAwareView):

    def get(self):
        callback=url_for('google_authorized', _external=True)
        return google.authorize(callback=callback)

class Logout(auth.UserAwareView):
    decorators = [login_required]

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

class Welcome(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('auth/welcome.html', **context)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token'), settings.FACEBOOK_APP_SECRET


class FacebookAuthorized(auth.UserAwareView):

    @facebook.authorized_handler
    def get(self, other):

        # Setting the oauth token in the session
        session['oauth_token'] = str(self.get('access_token', ''))

        # Receiving the user info from Facebook
        me = facebook.get('/me')

        # Checking for the user associated with the user's facebook ID
        user = auth_models.WTUser.get_user_by_facebook_id(me.data['id'])

        # If there is no record of this Facebook user logging in before, just make an account
        if not user:
            user = auth_models.WTUser(name=me.data['name'],
                                          facebook_id=me.data['id'],
                                          email=me.data['email'])
            user.put()

        # Log the user in
        if user:
            flask_login.login_user(user)

        return redirect('/')



class GoogleAuthorized(auth.UserAwareView):

    @google.authorized_handler
    def get(self, other):

        # Setting the oauth token in the session
        session['oauth_token'] = str(self.get('access_token', ''))
        access_token = session['oauth_token']

        from urllib2 import Request, urlopen, URLError

        headers = {'Authorization': 'OAuth '+ access_token}
        req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                      None, headers)
        try:
            res = urlopen(req)

            if res:
                output = json.loads(res.read())
                if 'email' in output:
                    email = output['email']

                if email:
                    user = auth_models.WTUser.get_user_by_email(email)

                if not user:
                    user = auth_models.WTUser(name=email,
                                              email=email)
                    user.save()

                if user:
                    flask_login.login_user(user)


        except URLError, e:
            if e.code == 401:
                # Unauthorized - bad token
                session.pop('access_token', None)
                return redirect(url_for('google_login'))
            return res.read()

        return redirect('/')


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token'), settings.FACEBOOK_APP_SECRET

@google.tokengetter
def get_access_token():
    return session.get('access_token'), settings.GOOGLE_SECRET
