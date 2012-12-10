from google.appengine.ext import db
from flask.templating import render_template
from tournament import models
from tournament import utils
from auth import auth_models
import json
from operator import attrgetter
import logging
import math
import uuid

def get_tournaments_by_user(user_key):
    tournaments = models.Tournament.all().filter('owner =', user_key).filter('order', 1).fetch(1000)
    tournaments.extend(models.Tournament.all().filter('admins', user_key).filter('order', 1).fetch(1000))
    t_set = set(tournaments)
    return t_set

def get_match_by_key(key):
    return db.get(key)

def get_participant_by_key(key):
    return db.get(key)

def get_tournament_by_id(id):
	return models.Tournament.get_by_id(id)

def get_tournament_by_key(key):
	return db.get(key)

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

def get_top_match_by_tournament(tournament):
    matches = models.Match.all().ancestor(tournament).fetch(limit=200)
    for match in matches:
        if not match.next_match:
            return match
    return None

def delete_tournament(tournament):
    keys_to_delete = db.Query(keys_only=True).ancestor(tournament).fetch(None)
    keys_to_delete.append(tournament.key())
    db.delete(keys_to_delete)

def update_match_by_winner(match_key, winner):
    # Get the selected match by id
    match = models.Match.get(match_key)
    participants = get_participants_by_match(match)
    # If there is a participant, then change the match status to played.
    # Add the winner to participants of the next match
    if winner in participants:
        match.status = models.Match.FINISHED_STATUS
        match.put()
        generate_player_to_match(winner, match.next_match)
        # Reload the view page
    return None

def update_match_with_player_score(match_key, participant, score):
    # Get the selected match by id
    match = models.Match.get(match_key)
    participants = get_participants_by_match(match)
    # If there is a participant, then change the match status to played.
    # Add the winner to participants of the next match
    for p in participants:
        if p.name == participant:
            p.score = score
            p.put()
    return None


def get_json_by_tournament(tournament):
    top_match = get_top_match_by_tournament(tournament)
    pickled = json.dumps(top_match, cls=models.MatchEncoder)
    tournament_winner = ''
    tournament_winner_key = ''
    if top_match.determine_winner():
        tournament_winner = top_match.determine_winner().name
        tournament_winner_key = str(top_match.determine_winner().key())
    tournament_json= {
        "title"     : tournament.name,
        "type"      : tournament.type,
        "created"   : tournament.created,
        "date"      : tournament.date,
        "location"  : tournament.location,
        "size"      : tournament.num_players,
        "matches"   : pickled
    }
    encoded = "{\"title\":\""+tournament.name+"\"," \
                "\"type\":\""+tournament.type+"\"," \
                "\"winner\":\""+tournament_winner+"\"," \
                "\"winner_key\":\""+tournament_winner_key+"\"," \
                "\"size\":\""+str(tournament.num_players)+"\"," \
                "\"matches\":"+pickled+"}"
    return encoded

# This method actually creates new paricipants and add it to the match
def generate_player_to_match(participant, cur_match):
    if isinstance(participant, models.Participant):
        newPlayer = models.Participant(
            seed=participant.seed,
            name=participant.name,
            parent=cur_match)
        newPlayer.put()
        cur_match.put()


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
                unique_player_id = str(uuid.uuid4())
                seeded_list.append({'name':value,'seed':int(num)+1,'unique_id':unique_player_id})

    t.num_players = len(seeded_list)
    t = t.put()

    ps_to_put = []
    #Round Robin Tournament Match Creation
    if form_data.get('type') == 'RR':
        def write_round(list_to_use, round_num, x0, x1, y0, y1):
            # start from x0 in list and move up to x1  in the list
            # start from y0 in list and move down to y1 in the list
            # pair each player element though each iteration
            for p1, p2 in zip(list_to_use[x0:x1:1],list_to_use[y0:y1:-1]): 
                m = models.Match(round=round_num, status=models.Match.NOT_STARTED_STATUS, parent=t)
                m.put()
                player_1 = models.Participant(name=p1['name'],uuid=p1['unique_id'],parent=m)
                player_2 = models.Participant(name=p2['name'],uuid=p2['unique_id'],parent=m)
                ps_to_put.extend([player_1, player_2])

        size = len(seeded_list)
        split = size/2

        # loop through the list for the number of rounds we need
        # while shuffling the players to create rounds
        for r in range(size-1):
            write_round(seeded_list,r+1,0,split,size,split-1)# create new round
            seeded_list.append(seeded_list.pop(1))# shuffle list

        # if odd num of players we need to create a new round where we exclude the first player in
        # the above loop, if odd, we at least exclude one player per round, except the first player
        # due to the nature of round robins and the algorithm 
        if size%2 != 0:
            write_round(seeded_list,r+2,1,split+1,size,split-1)

    #Single Elimination Tournament Match Creation
    elif form_data.get('type') == 'SE':

        seed_dict = dict([(player['seed'],player['name'])
                          for player in seeded_list])
        logging.debug("Seed_Dict= %s" % seed_dict)

        num_players = len(seeded_list)
        bracket_array = utils.determine_bracket(num_players)
        logging.debug("Bracket Array= %s" % bracket_array)

        def create_match(bracket_array, next_match, round=1):
            """
            Creates one match, and then decides if it should create participants or call this
            function again, passing along the newly created match as the next match.
            :param bracket_array: list representing all or part of the bracket depending
                                  on recursion depth.
            :param next_match: The match acting as the parent of the match we create.
            :param round: We only need this so that we can set it in the match. It isn't used in
                          recursion logic at all.
            :return: Nothing
            """
            if not bracket_array or len(bracket_array) > 2:
                raise TypeError("Malformed bracket array. Length=%s" % len(bracket_array))

            m = models.Match(round = round,
                             status = models.Match.NOT_STARTED_STATUS,
                             parent = t,
                             next_match = next_match)
            m.put()
            if next_match:
                next_match.add_children_match(m)

            p_logs = []
            for item in bracket_array:
                #item could be an int or a list.
                #if it is a list, we just want to call this function recursively until it is an int.
                #if it is an int, we create a participant. The item is the seed.
                if type(item) == int:
                    p = models.Participant(seed=item,
                                           name=seed_dict[item],
                                           uuid=str(uuid.uuid4()),
                                           parent=m)
                    ps_to_put.append(p)
                    p_logs.append(item)
                elif type(item) == list:
                    create_match(item, m, round+1)
                else:
                    raise TypeError("Unexpected type in bracket array. Type=%s" % type(item))

            logging.info(utils.print_match(m, p_logs))
            return

        create_match(bracket_array, None)
    db.put(ps_to_put)
    return t


def get_round_robin_rounds(tournament):
    matches = get_matches_by_tournament(tournament)
    rounds = {}
    for match in matches:
        participants = get_participants_by_match(match)
        if match.round in rounds:
            rounds.get(match.round).append((match,participants))
        else:
            rounds[match.round] = [(match,participants)]

    tuple_list = list(rounds.items())
    sorted_list = sorted(tuple_list)
    return sorted_list


def get_non_private_tournaments():
    keys = models.Tournament.all(keys_only=True).filter("perms =", models.Tournament.PUBLIC).fetch(1000)
    more_keys = models.Tournament.all(keys_only=True).filter("perms =", models.Tournament.PROTECTED).fetch(1000)

    keys.extend(more_keys)

    tournaments = db.get(keys)
    return tournaments

def get_public_tournaments():
    keys = models.Tournament.all(keys_only=True).filter("perms =", models.Tournament.PUBLIC).fetch(1000)
    tournaments = db.get(keys)
    return tournaments


def get_participants_from_match(key):
    participants = models.Participant.parent(key).fetch()
    return participants

def get_participants_by_uuid(uuid):
    return models.Participant.all().filter(unique_id=uuid)

def get_round_robin_standings(tournament):
    uuids = {}
    participants = models.Participant.all().ancestor(tournament)
    for par in participants:
        if par.uuid in uuids:
            uuids.get(par.uuid).append(par)
        else:
            uuids[par.uuid] = [par]

    standings = []
    for uuid,pars in uuids.items():
        wins = 0
        lose = 0
        for par in pars:
            if par.parent().has_been_played():
                if par.is_winner():
                    wins += 1
                else:
                    lose += 1
        standings.append((wins,lose,par.name,par.uuid))
    standings.sort(reverse=True)
    return standings
