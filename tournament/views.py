from flask import request
from flask.templating import render_template

from lib.flask_login import login_required

import auth
import forms
import models
import actions

class New_Tournament(auth.UserAwareView):
    def get(self):
        context = self.get_context({
            'fields':{'step':1},
        })

        return self.render_new_tourney(context)

    def post(self):
        context = self.get_context({'fields':{}})
        step = int(request.form.get('step'))
        if step == 1:
            form = forms.NewTournamentStep1(request.form)
            if form.validate():
                context['fields'].update(form.data)
                context['fields'].update({'step':2})
                context['form'] = forms.NewTournamentStep2(prefix="step2")
                return self.render_new_tourney(context)
            else:
                return self.render_new_tourney({'fields':{'step':1}, 'form':form})
        elif step == 2:
            form = forms.NewTournamentStep2(request.form, prefix="step2")
            if form.validate():
                context['fields'].update(form.data)
                context['fields'].update({
                    'tournament_security':request.form.get('tournament_security')})
                context['fields'].update({'step':3})
                context['form'] = forms.NewTournamentStep3(prefix="step3")
                #TODO finish processing

                return self.render_new_tourney(context)
            else:
                return self.render_new_tourney({'fields':{'step':2}, 'form':form})
        elif step == 3:
            pass

    #Made this so I don't have to type the template a bunch of times
    def render_new_tourney(self, context):
        if 'fields' in context:
            step = context['fields'].get('step', 1)
        else:
            step = 1
        return render_template('new_tournament/new_tournament_%s.html' % step, **context)


class Tournament_List(auth.UserAwareView):
    decorators = [login_required]

    def get(self):
        context = self.get_context()
        context['user_events'] = actions.get_events_by_user(self.user)
        return render_template('user_tournament_list.html', **context)
