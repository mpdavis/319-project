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
        step = int(self.request.POST.get('step'))
        if step == 1:
            form = forms.NewTournamentStep1(self.request.POST)
            if form.validate():
                context['fields'].update(form.data)
                context['fields'].update({'step':2})
                context['form'] = forms.NewTournamentStep2()
                self.render_new_tourney(context)
            else:
                self.render_new_tourney({'fields':{'step':1}, 'form':form})
        elif step == 2:
            form = forms.NewTournamentStep2(self.request.POST)
            if form.validate():
                context['fields'].update(form.data)
                context['fields'].update({
                    'tournament_security':self.request.POST.get('tournament_security')})
                context['fields'].update({'step':3})
                context['form'] = forms.NewTournamentStep3()
                self.render_new_tourney(context)
            else:
                self.render_new_tourney({'fields':{'step':2}, 'form':form})
        elif step == 3:
            pass

    #Made this so I don't have to type the template a bunch of times
    def render_new_tourney(self, context):
        if 'fields' in context:
            step = context['fields'].get('step', 1)
        else:
            step = 1
        self.render_response('new_tournament/new_tournament_%s.html' % step, context)