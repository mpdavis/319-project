import sys, os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
sys.path.insert(0, LIB_PATH)

from google.appengine.ext.webapp.util import run_wsgi_app

from flask import Flask
from flask.templating import render_template

import auth
from auth import urls as auth_urls

from tournament import urls as tournament_urls
from tournament.templatetags import ttags


app = Flask(__name__)

auth.initialize(app)

app.secret_key = 'this-is-just-our-dev-key-oh-so-secret'


class MainHandler(auth.UserAwareView):
    def get(self):
        context = self.get_context()

        if self.user:
            context['username'] = self.user.username

        return render_template('home.html', **context)


#Define URLs
app.add_url_rule('/', view_func=MainHandler.as_view('home'))
auth_urls.setup_urls(app)
tournament_urls.setup_urls(app)

#Setup other things
ttags.setup_jinja2_environment(app)


if __name__ == '__main__':
    #Add the lib directory to the path
    run_wsgi_app(app)

