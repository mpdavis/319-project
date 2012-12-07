from wtforms import Form, TextField, PasswordField, BooleanField, HiddenField
from wtforms import validators

class SignupForm(Form):
    username = TextField('Username',
        [validators.Required()])
    email = TextField('Email',
        [validators.Required(),
         validators.Email()])
    password = PasswordField('Password',
        [validators.Required(),
         validators.EqualTo('password_confirm',
             message="Passwords must match.")])
    password_confirm = PasswordField('Confirm Password',
        [validators.Required()])

class LoginForm(Form):
    email = TextField('Email',
        [validators.Required(), validators.Email()])
    password = PasswordField('Password',
        [validators.Required()])
    remember_me = BooleanField('Remember')

class ForgotPasswordForm(Form):
    email = TextField('Email',
                      [validators.Required(), validators.Email()])

class ResetPasswordForm(Form):
    password = PasswordField('Password',
                             [validators.Required(),
                              validators.EqualTo('password_confirm',
                                                 message="Passwords must match.")])
    password_confirm = PasswordField('Confirm Password',
                                     [validators.Required()])
    token = HiddenField()