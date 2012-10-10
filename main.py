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


import auth
from auth import views as auth_views

import tournament
from tournament import views as tournament_views


class MainHandler(auth.UserAwareHandler):
    def get(self):
        context = dict()

        if self.user:
            context['username'] = self.user.username

        self.render_response('home.html', context)


app = webapp2.WSGIApplication([

    webapp2.Route('/', MainHandler, 'home'),

    webapp2.Route('/auth/login', auth_views.login, 'login'),
    webapp2.Route('/auth/logout', auth_views.logout, 'logout'),
    webapp2.Route('/auth/register', auth_views.register, 'register'),
    webapp2.Route('/auth/check_username', auth_views.check_username, 'check_username'),

    webapp2.Route('/tournament/new', tournament_views.new_tournament, 'new-tourney'),

                                ],
                              debug=True)
#template.register_template_library('tournament.templatetags.ttags')