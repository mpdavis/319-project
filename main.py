import sys, os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
sys.path.insert(0, LIB_PATH)

from google.appengine.ext.webapp.util import run_wsgi_app

from flask import Flask
from flask.templating import render_template
from flask import request

import auth
from auth import urls as auth_urls

from tournament import urls as tournament_urls
from tournament.templatetags import ttags


app = Flask(__name__)

auth.initialize(app)

app.secret_key = 'this-is-just-our-dev-key-oh-so-secret'


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

        return render_template('demo.html', **context)


#Define URLs
app.add_url_rule('/', view_func=MainHandler.as_view('home'))
app.add_url_rule('/demo/', view_func=DemoHandler.as_view('demo'))
auth_urls.setup_urls(app)
tournament_urls.setup_urls(app)

#Setup other things
ttags.setup_jinja2_environment(app)


if __name__ == '__main__':
    #Add the lib directory to the path
    run_wsgi_app(app)

