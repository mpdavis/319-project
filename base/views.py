from flask import request, redirect, url_for, jsonify
from flask.templating import render_template

import logging
import auth

class About(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('about.html',**context)

class ContactUs(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('contact.html',**context)
