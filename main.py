#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2

from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from auth import views as auth_views
from auth import models as auth_models
import auth


class MainHandler(auth.UserAwareHandler):
    def get(self):
        context = dict()

        if self.user:
            import logging
            logging.warning(self.user_model)
            context['username'] = self.user_model.username

        path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
        self.response.out.write(template.render(path, context))


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'zomg-this-key-is-so-secret',
    }


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, 'home'),
    webapp2.Route('/auth/login', auth_views.login, 'login'),
    webapp2.Route('/auth/logout', auth_views.logout, 'logout'),
    webapp2.Route('/auth/register', auth_views.register, 'register'),

                                ],
                              debug=True, config=config)
