from google.appengine.ext import db

from tournament import models
from auth import auth_models

import logging


def get_tournaments_by_user(user_key):
    tournaments = models.Tournament.all().filter('owner =', user_key).filter('order', 1).fetch(1000)
    tournaments.extend(models.Tournament.all().filter('admins', user_key).filter('order', 1).fetch(1000))
    t_set = set(tournaments)
    return t_set

def get_tournament_by_id(id):
	return models.Tournament.get_by_id(id)

def get_user_by_id(id):
    return auth_models.WTUser.get_by_id(id)

def get_user_by_email(email):
    user = auth_models.WTUser.all().filter('email =', email).fetch(1)
    if user:
        return user[0]
    return None

def get_linked_tournaments(tournament):
    linked = []
    t = tournament
    while True:
        if t.next_tournament:
            linked.append(t.next_tournament)
            t = t.next_tournament
        else:
            break
    return linked

def get_matches_by_tournament(tournament, limit = 200):
    matches = models.Match.all().ancestor(tournament).fetch(limit)
    return matches

def get_participants_by_match(match, limit = 200):
    participants = models.Participant.all().ancestor(match).fetch(limit)
    return participants

def get_json_by_tournament(tournament):
    
    def participants_to_bracket(participants, match_size):
        if len(participants) > match_size and match_size > 1:
            matches = []
            for i in range(len(participants) / match_size):
                matches.append(participants[(i*match_size):((i+1)*match_size)])
            remainder = len(participants) % match_size
            if remainder > 0:
                matches.append(participants[((-1)*remainder):])
            matches = participants_to_bracket(matches, match_size)
        else:
            matches = participants
        return matches
    
    def bracket_to_json(bracket):
        assert (type(bracket) == list) and (len(bracket) > 0), \
            "Invalid hierarchal bracket list format."
        json_format = {"winner":"?"}
        if type(bracket[0]) == list:
            for i in range(len(bracket)):
                json_format["tier_%s" % str(i)] = bracket_to_json(bracket[i])
        else:
            for i in range(len(bracket)):
                json_format["player_%s" % str(i)] = bracket[i]
        return json_format
    
    # Grab all participants
    all_participants = []
    matches = get_matches_by_tournament(tournament)
    for match in matches:
        participants = get_participants_by_match(match)
        all_participants.extend(participants)
    all_participants.sort(key=lambda x: x.seed, reverse=False)
    
    # Pair by seeds
    participant_names = []
    for i in range(len(all_participants)/2):
        participant_names.append(all_participants[i].name)
        participant_names.append(
            all_participants[len(all_participants)-1-i].name)
    
    # NOTE: Currently only supports matches of two players each.
    bracket = participants_to_bracket(participant_names, 2)
    return bracket_to_json(bracket)

def create_tournament(form_data, p_form_data, user):
    t = models.Tournament(
        name=form_data.get('name'),
        date=form_data.get('date'),
        location=form_data.get('location'),
        owner=user,
        perms=form_data.get('tournament_security'),
        type=form_data.get('type'),
        order=1,
        win_method=models.Tournament.HIGHEST_WINS)
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
                parent=m)
            ps_to_put.append(p1)

        if l['seed'] is not None and l['name'] is not None:
            p2 = models.Participant(
                seed=l['seed'],
                name=l['name'],
                parent=m)
            ps_to_put.append(p2)


    db.put(ps_to_put)
