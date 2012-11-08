from google.appengine.ext import db

from tournament import models
from auth import auth_models

import logging


def get_events_by_user(user):
    events = models.Event.all().filter('owner =', user).fetch(200)
    #TODO: account for the admins who should also be able to see the event in their list.
    return events

def get_event_by_id(id):
	return models.Event.get_by_id(id)

def get_user_by_id(id):
    return auth_models.WTUser.get_by_id(id)

def get_user_by_email(email):
    user = auth_models.WTUser.all().filter('email =', email).fetch(1)
    if user:
        return user[0]
    return None

def get_tournaments_by_event(event, limit = 200):
    tournaments = models.Tournament.all().ancestor(event).fetch(limit)
    return tournaments

def get_matches_by_tournament(tournament, limit = 200):
    matches = models.Match.all().ancestor(tournament).fetch(limit)
    return matches

def get_participants_by_match(match, limit = 200):
    participants = models.Participant.all().ancestor(match).fetch(limit)
    return participants

def create_tournament(form_data, p_form_data, user):
    e = models.Event(
        name=form_data.get('name'),
        date=form_data.get('date'),
        location=form_data.get('location'),
        owner=user,
        perms=form_data.get('tournament_security'))
    e.put()
    t = models.Tournament(
        type=form_data.get('type'),
        order=0,
        win_method=models.Tournament.HIGHEST_WINS,
        parent=e)
    t.put()

    seeded_list = []
    if form_data.get('show_seeds', False):
        name_dict = {}
        seeds_dict = {}

        for field, value in p_form_data.items():
            if 'seed' in field:
                num = field[11:-4]
                seeds_dict[int(num)] = value
            if 'name' in field:
                num = field[11:-4]
                name_dict[int(num)] = value

        seeded_list = [{'name':None,'seed':None}]*len(seeds_dict)
        for i in range(len(seeds_dict)):
            seed_index = seeds_dict[i]
            if seed_index is not None:
                seeded_list[seed_index-1] = {'name':name_dict[i],'seed':seeds_dict[i]}
    else:
        for field, value in p_form_data.items():
            if 'name' in field:
                num = field[11:-4]
                seeded_list.append({'name':value,'seed':int(num)})  

    if len(seeded_list) % 2 == 1:
        seeded_list.append({'name':None,'seed':None})
    
    upper = seeded_list[:len(seeded_list)/2]
    lower = seeded_list[len(seeded_list)/2:]
    lower.reverse()

    ps_to_put = []
    round = 1
    for u,l in zip(upper,lower):
        m = models.Match(round=round, has_been_played=False, parent=t)
        m.put()
        round +=1
        if u['seed'] is not None and u['name'] is not None:
            p1 = models.Participant(
                seed=u['seed'],
                name=u['name'],
                event_key=e.key(),
                parent=m)
            ps_to_put.append(p1)

        if l['seed'] is not None and l['name'] is not None:
            p2 = models.Participant(
                seed=l['seed'],
                name=l['name'],
                event_key=e.key(),
                parent=m)
            ps_to_put.append(p2)


    db.put(ps_to_put)
