import os
from google.appengine.ext.webapp import template

import auth

class new_tournament(auth.UserAwareHandler):
    def get(self):
        context = {} #move this to a utils fuction?

        self.render_response('templates/new_tournament.html', context)

    def post(self):
        pass