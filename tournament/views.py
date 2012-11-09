from flask import request, redirect, url_for
from flask.templating import render_template

import json
from operator import attrgetter
from lib.flask_login import login_required

import wtforms
import auth
import forms
import models
import actions

import logging

class New_Tournament(auth.UserAwareView):
    def get(self):
        context = self.get_context({
            'fields':{'step':1},
        })

        return self.render_new_tourney(context)

    def post(self):
        #Initialize context with empty fields dicts. We pass values from one step to the next in the
        #fields dict, which is rendered as hidden inputs and comes back in request.form in each step
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
            step1form = forms.NewTournamentStep1(request.form)
            context['fields'].update(step1form.data)
            if form.validate():
                context['fields'].update(form.data)
                context['fields'].update({'step':3})
                context['form'] = forms.NewTournamentStep3(prefix="step3")
                return self.render_new_tourney(context)
            else:
                context.update({'fields':{'step':2}, 'form':form})
                return self.render_new_tourney(context)
        elif step == 3:
            form = forms.NewTournamentStep3(request.form, prefix="step3")
            step2form = forms.NewTournamentStep2DATEHACK(request.form)
            step1form = forms.NewTournamentStep1(request.form)
            context['fields'].update(step2form.data)
            context['fields'].update(step1form.data)
            if form.validate():
                context['fields'].update(form.data)
                num_participants = context['fields'].get('number_participants')
                include_seeds = context['fields'].get('show_seeds')

                p_form = forms.handle_participant_forms(request.form,num_participants,include_seeds)
                p_form.validate() #TODO: if here?

                actions.create_tournament(context['fields'], p_form.data, self.user.key())

                #TEMP REDIRECT TO HOME TODO: Redirect to Tournament Overview Page once it exists
                return redirect(url_for('event-list'))
            else:
                context.update({'fields':{'step':3}, 'form':form})
                return self.render_new_tourney(context)

    #Made this so I don't have to type the template a bunch of times
    def render_new_tourney(self, context):
        if 'fields' in context:
            step = context['fields'].get('step', 1)
        else:
            step = 1
        return render_template('new_tournament/new_tournament_%s.html' % step, **context)


class Tournament_List(auth.UserAwareView):
    decorators = [login_required]
    active_nav = 'my_tournaments'

    def get(self):
        context = self.get_context()
        context['user_tournaments'] = actions.get_tournaments_by_user(self.user)
        return render_template('user_tournament_list.html', **context)

class Tournament_Edit(auth.UserAwareView):
    decorators = [login_required]

    def get(self):
        context = self.get_context()

        event_id = request.args.get('id')
        event = actions.get_event_by_id(int(event_id))
        html_to_show = ""

        # if event belongs to our user allow them to edit else redirect them
        if context['user'].key().id() == event.owner.key().id():

            # preload our forms with data
            form = forms.EditTournament()
            form.name.data = event.name
            form.date.data = event.date
            form.location.data = event.location
            form.tournament_security.data = event.perms

            admin_list = [actions.get_user_by_id(admin_key.id()) for admin_key in event.admins]

            tournaments = actions.get_tournaments_by_event(event)

            matches = []
            for tournament in tournaments:
                matches.extend(actions.get_matches_by_tournament(tournament))

            participants = []
            participants_by_match = {}
            for match in matches:
                found_participants = actions.get_participants_by_match(match)
                participants_by_match[match] = found_participants
                participants.extend(found_participants)

            participants.sort(key=attrgetter('seed')) 

            context['event'] = event
            context['tournaments'] = tournaments
            context['matches'] = matches
            context['participants'] = participants
            context['participants_by_match'] = participants_by_match
            context['admins'] = admin_list
            context['form'] = form

            html_to_show = render_template('edit_tournament.html', **context)
        else:
            html_to_show = render_template('home.html',**context)# need to redirect to another page

        return html_to_show

    def post(self):
        form = forms.EditTournament(request.form)
        error = 0

        event_id = request.args.get('id')
        event = actions.get_event_by_id(int(event_id))

        if event is not None:
            if form.validate():
                new_admins = request.args.get('new_admins').split(":")
                event.admins = [actions.get_user_by_email(new_guy).key() for new_guy in new_admins if new_guy != ""]

                event.name = form.name.data
                event.date = form.date.data
                event.location = form.location.data
                event.perms = form.tournament_security.data
                event.put()
            else:
                error = 2
        else:
            error = 1

        return json.dumps({'error': error})

class Tournament_View(auth.UserAwareView):
    # TODO: Make perms work
    decorators = [login_required]
    
    def get(self):
        context = self.get_context()
        
        event_id = request.args.get('id')
        event = actions.get_event_by_id(int(event_id))
        
        tournament = actions.get_tournaments_by_event(event)[0]
        bracket_json = actions.get_json_by_tournament(tournament)
        
        context['bracket_json'] = bracket_json
        return render_template('view_tournament.html', **context)

class check_email(auth.UserAwareView):
    def get(self):
        email = request.args.get('email', None)

        output = {"exists" : False, "username" : None, "email" : email}
        found_user = actions.get_user_by_email(email)


        if found_user is not None:
            output['exists'] = True
            output['username'] = found_user.username

        return json.dumps(output)
