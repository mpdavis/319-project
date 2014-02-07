from flask import request, redirect, url_for, jsonify
from flask.templating import render_template

import logging
import auth


class MainHandler(auth.UserAwareView):
    active_nav = 'home'

    def get(self):
        context = self.get_context()

        context['remove_header'] = True

        if self.user:
            context['username'] = self.user.username

        context['login_mode'] = request.args.get('login_mode', None)

        return render_template('home.html', **context)


class DemoHandler(auth.UserAwareView):
    active_nav = 'home'

    def get(self):
        context = self.get_context()
        context['demo'] = demo_content
        return render_template('demo.html', **context)


class About(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('about.html',**context)


class ContactUs(auth.UserAwareView):
    def get(self):
        context = self.get_context()
        return render_template('contact.html',**context)
