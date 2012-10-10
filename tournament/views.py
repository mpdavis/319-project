import os
from google.appengine.ext.webapp import template

import auth
import forms
import logging

class new_tournament(auth.UserAwareHandler):
    def get(self):
        context = {
            'fields':{'step':1},
        }
        self.render_new_tourney(context)

    def post(self):
        context = {'fields':{}}
        form = forms.NewTournamentStep1(self.request.POST)
        if form.validate():
            context['fields'].extend(form.data)
            context['fields'].update({'step':2})
            self.render_new_tourney(context)
        else:
            self.render_new_tourney({'fields':{'step':1}, 'form':form})

    #Made this so I don't have to type the template a bunch of times
    def render_new_tourney(self, context):
        if 'fields' in context:
            step = context['fields'].get('step', 1)
        else:
            step = 1
        self.render_response('templates/new_tournament/new_tournament_%s.html' % step, context)