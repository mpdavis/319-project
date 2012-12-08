import sys, os

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
sys.path.insert(0, LIB_PATH)

from google.appengine.ext.webapp.util import run_wsgi_app

from flask import Flask

import auth
from auth import urls as auth_urls

from tournament import urls as tournament_urls
from tournament.templatetags import ttags

from base import urls as base_urls


app = Flask(__name__)

auth.initialize(app)

app.secret_key = 'this-is-just-our-dev-key-oh-so-secret'


#Define URLs
base_urls.setup_urls(app)
auth_urls.setup_urls(app)
tournament_urls.setup_urls(app)

#Setup other things
ttags.setup_jinja2_environment(app)


if __name__ == '__main__':
    #Add the lib directory to the path
    run_wsgi_app(app)

