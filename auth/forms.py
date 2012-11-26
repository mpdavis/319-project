from wtforms import Form, TextField, PasswordField, BooleanField
from wtforms import validators
from base import forms as base_forms

class SignupForm(base_forms.BaseForm):
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

class LoginForm(base_forms.BaseForm):
    email = TextField('Email',
        [validators.Required(), validators.Email()])
    password = PasswordField('Password',
        [validators.Required()])
    remember_me = BooleanField('Remember Me')