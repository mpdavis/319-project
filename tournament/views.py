from flask import request, redirect, url_for, jsonify
from flask.templating import render_template
from google.appengine.ext import db
import json
from operator import attrgetter
from lib.flask_login import login_required

from tournament import public_tournament

import wtforms
import auth
import forms
import models
import actions
import flask

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
                return redirect(url_for('tournament-list'))
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

    def get(self, tournament_key):
        context = self.get_context()

        tournament = actions.get_tournament_by_key(tournament_key)
        admin_list = [actions.get_user_by_id(admin_key.id()) for admin_key in tournament.admins]

        html_to_show = ""
        owners = [tournament.owner.key().id()]
        owners.extend([admin.key().id() for admin in admin_list])

        # if event belongs to our user allow them to edit else redirect them
        if context['user'].key().id() in owners:

            # preload our forms with data
            form = forms.EditTournament()
            form.name.data = tournament.name
            form.date.data = tournament.date
            form.location.data = tournament.location
            form.tournament_security.data = tournament.perms
            # form.type.data = tournament.type
            # form.order.data = tournament.order
            form.win_method.data = str(tournament.win_method)


            tournaments = actions.get_linked_tournaments(tournament)

            matches = []
            matches.extend(actions.get_matches_by_tournament(tournament))


            participants = []
            participants_by_match = {}
            for match in matches:
                found_participants = actions.get_participants_by_match(match)
                participants.extend(found_participants)

                while(len(found_participants)<2):
                    found_participants.append({'name':'To Be Determined'})
                
                participants_by_match[match] = found_participants

            if tournament.type == 'RR':
                # in round robins we have multiple participants who are identified by 
                # their name, which means we will have several participant models with the same name 
                # what we are doing here is making sure when a user is looking at a tourney edit page
                # we only display one player instead of the same player over and over again
                participants = [v for v in {part.name:part for part in participants}.itervalues()]

            matches.sort(key=attrgetter('round'))
            participants.sort(key=attrgetter('seed')) 

            context['tournament'] = tournament
            context['linked_tournaments'] = tournaments
            context['matches'] = matches
            context['participants'] = participants
            context['participants_by_match'] = participants_by_match
            context['admins'] = admin_list
            context['form'] = form

            html_to_show = render_template('edit_tournament.html', **context)
        else:
            html_to_show = render_template('home.html',**context)# need to redirect to another page

        return html_to_show

    def post(self,tournament_key):
        form = forms.EditTournament(request.form)
        error = 0

        tournament = actions.get_tournament_by_key(tournament_key)

        if tournament is not None:
            if form.validate():
                new_admins = request.args.get('new_admins','').split(":")
                tournament.admins = [actions.get_user_by_email(new_guy).key() for new_guy in new_admins if new_guy != ""]

                tournament.name = form.name.data
                tournament.date = form.date.data
                tournament.location = form.location.data
                tournament.perms = form.tournament_security.data
                # tournament.type = form.type.data
                # tournament.order = form.order.data
                tournament.win_method = int(form.win_method.data)

                tournament.put()
            else:
                error = 2
        else:
            error = 1

        return json.dumps({'error': error})


class Tournament_View(auth.UserAwareView):
    # TODO: Make perms work
    # decorators = [login_required]
    
    def get(self, tournament_key):
        #Contextual variables used by all tournament types.
        context = self.get_context()
        context['tournament_key'] = tournament_key
        context['full_page_content'] = True
        tournament = actions.get_tournament_by_key(tournament_key)
        context['num_players'] = str(tournament.num_players)
        context['tournament'] = tournament

        admin_list = []
        is_a_owner = False
        if context['user'] is not None:
            admin_list = [actions.get_user_by_id(admin_key.id()) for admin_key in tournament.admins]
            owners = [tournament.owner.key().id()]
            owners.extend([admin.key().id() for admin in admin_list])
            is_a_owner = context['user'].key().id() in owners

        if tournament:
            if tournament.perms == tournament.PRIVATE and is_a_owner or tournament.perms != tournament.PRIVATE:
                if tournament.type == models.Tournament.ROUND_ROBIN:
                    #Setup context for Round Robin tournament
                    context['round_robin_rounds'] = actions.get_round_robin_rounds(tournament)
                    return render_template('view_round_robin.html', **context)
                else:
                    #Setup context for bracket-style tournaments
                    return render_template('view_tournament.html', **context)

        return flask.abort(404)

# We will use this view for non-logged in users accessing a public tournament.
# Prevents them from being able to view other tournaments that are not public.
class PublicTournamentView(Tournament_View):
    decorators = [public_tournament]


class Tournament_Json(auth.UserAwareView):
    # TODO: Make perms work
    # decorators = [login_required]
    
    def get(self, tournament_key):
        tournament = actions.get_tournament_by_key(tournament_key)
        bracket_json = actions.get_json_by_tournament(tournament)
        return bracket_json


class Tournament_Search(auth.UserAwareView):
    active_nav = 'tournament_search'
    def get(self):
        context = self.get_context()
        context['tournaments'] = actions.get_public_tournaments()
        return render_template('search_tournament.html', **context)


class check_email(auth.UserAwareView):
    def get(self):
        email = request.args.get('email', None)

        output = {"exists" : False, "username" : None, "email" : email}
        found_user = actions.get_user_by_email(email)


        if found_user is not None:
            output['exists'] = True
            output['username'] = found_user.username

        return json.dumps(output)


class get_latest_tournaments(auth.UserAwareView):
    def get(self):
        return actions.get_datatables_records(request)

class delete_tournament(auth.UserAwareView):
    def post(self):
        context = self.get_context()
        tournament_key = request.args.get('tournament_key',None)
        fail = False

        if tournament_key is not None:

            tournament = actions.get_tournament_by_key(tournament_key)
            
            admin_list = [actions.get_user_by_id(admin_key.id()) for admin_key in tournament.admins]
            owners = [tournament.owner.key().id()]
            owners.extend([admin.key().id() for admin in admin_list])

            if context['user'].key().id() in owners:
                actions.delete_tournament(tournament)
            else:
                fail = True
        else:
            fail = True



        return json.dumps({'fail':fail})


class update_match(auth.UserAwareView):
    def get(self):
        # Please feed me this json.
        # {'match':{'match_key':'key_for_match', 'match_status':1, 
        #           'player1':{'key':'p1_key', 'score':12},
        #           'player2':{'key':'p2_key', 'score':12}}}
        logging.warning("test")
        p1_score = p2_score = p1_key = p2_key = winner_key = next_key = 0
        data = json.loads(json.dumps(request.args))

        match = actions.get_match_by_key(data['match[match_key]'])
        match_participants = actions.get_participants_by_match(match)

        logging.warning(match)
        if match.status < 1:
            logging.warning(long(data['match[match_status]']))
            match.status =  long(data['match[match_status]'])
            next_key = str(match.next_match.key())
            to_put = [match]

            if 'match[player1][key]' in data:
                p1 = actions.get_participant_by_key(data['match[player1][key]'])
                p1_key = p1.key()
                p1_score = p1.score = float(data['match[player1][score]'])
                to_put.append(p1)
            else:
                p1_key = match_participants[0].key()
                p1_score = match_participants[0].score

            if 'match[player2][key]' in data:
                p2 = actions.get_participant_by_key(data['match[player2][key]'])
                p2_key = p2.key()
                p2_score = p2.score = float(data['match[player2][score]'])
                to_put.append(p2)
            else:
                p2_key = match_participants[1].key()
                p2_score = match_participants[1].score

            winner_key = None
            if match.status == 1:
                # Match is over, determine a winner
                winner = match.determine_winner()
                if winner:
                    to_put.append(models.Participant(
                                        seed=winner.seed,
                                        name=winner.name,
                                        parent=match.next_match))
                    winner_key = winner.key()

            db.put(to_put)

        return json.dumps({'p1_score':p1_score, 'p1_key': str(p1_key), 'p2_score':p2_score, 'p2_key': str(p2_key), 'winner': str(winner_key), 'next_match': next_key})

