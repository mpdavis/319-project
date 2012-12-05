from google.appengine.ext import db
from flask.templating import render_template
from tournament import models
from auth import auth_models
import json
from operator import attrgetter
import logging
import math

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
    tournament_json= {
        "title"     : tournament.name,
        "type"      : tournament.type,
        "created"   : tournament.created,
        "date"      : tournament.date,
        "location"  : tournament.location,
        "size"      : tournament.num_players,
        "matches"   : pickled
    }
    encoded = "{\"title\":\""+tournament.name+"\",\"type\":\""+tournament.type+"\",\"size\":\""+str(tournament.num_players)+"\",\"matches\":"+pickled+"}"
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
                seeded_list.append({'name':value,'seed':int(num)+1})

    t.num_players = len(seeded_list)
    t = t.put()

    ps_to_put = []
    if form_data.get('type') == 'RR':
        def write_round(list_to_use, round_num, x0, x1, y0, y1):
            # start from x0 in list and move up to x1  in the list
            # start from y0 in list and move down to y1 in the list
            # pair each player element though each iteration
            for p1, p2 in zip(list_to_use[x0:x1:1],list_to_use[y0:y1:-1]): 
                m = models.Match(round=round_num, status=models.Match.NOT_STARTED_STATUS, parent=t)
                m.put()
                player_1 = models.Participant(name=p1['name'],parent=m)
                player_2 = models.Participant(name=p2['name'],parent=m)
                ps_to_put.extend([player_1, player_2])

        size = len(seeded_list)
        split = size/2

        # loop through the list for the number of rounds we need
        # while shuffling the players to create rounds
        for r in range(size-1):
            write_round(seeded_list,r+1,0,split,size,split-1)# create new round
            seeded_list.append(seeded_list.pop(1))# shuffle list

        # if odd num of players we need to create a new round where we exclude the first player
        # in the above loop, if odd, we at least exclude one player per round, except the first player
        # due to the nature of round robins and the algorithm 
        if size%2 != 0:
            write_round(seeded_list,r+2,1,split+1,size,split-1)

    ###### The odd number of participants is not working properly.
    elif form_data.get('type') == 'SE':
        # I couldn't fit this into the build tourney recursion, however this helps decides the round number for
        # each match. This method associates each round number with the level of recursion.
        # for example a tourney of 16 people
        # 0:[15] 
        # 1:[14, 13] 
        # 2:[12, 11, 10, 9] 
        # 3:[8, 7, 6, 5, 4, 3, 2, 1]
        # so each each time we create a new match we just pop an element off of the list depedning on our level of
        # recursion  
        def decide_rounds(dict_to_fill, num_of_rounds, level=0):
            if num_of_rounds <=0:
                return
            step = num_of_rounds-int(math.pow(2,level))
            if step<0: 
                step=0
            dict_to_fill[level] = [i for i in range(num_of_rounds, step, -1)]
            decide_rounds(dict_to_fill,step,level+1)

        round_dict = {}
        decide_rounds(round_dict,len(seeded_list)-1)


        # rec_build_matches populates our tourneys with the correct network of matches
        def build_matches_helper(next_match, is_odd, level=0, round =1):
            logging.info('level: %d, next_match: %s,   %s', level, next_match, round_dict[level])
            def write_player(seededd_list, cur_match):
                if len(seeded_list) > 0:
                    if len(seeded_list)%2==1:
                        player = seeded_list.pop()
                    else:
                        player = seeded_list[0]
                        seeded_list.remove(player)
                    if player is not None and player['seed'] is not None and player['name'] is not None:
                        p1 = models.Participant(
                            seed=player['seed'],
                            name=player['name'],
                            parent=cur_match)
                        logging.info('player: %s is added to %d', p1.name, cur_match.key().id())
                        ps_to_put.append(p1)

            m = models.Match(round=round, status=models.Match.NOT_STARTED_STATUS, parent=t, next_match = next_match)
            m.put()
            is_leaf = True

            if next_match:
                next_match.add_children_match(m)

            if round_dict.has_key(level+1):
                candidates = []
                if len(round_dict[level+1])>1:
                    candidates.append(round_dict[level+1].pop())
                    candidates.append(round_dict[level+1].pop())
                elif len(round_dict[level+1])>0:
                    candidates.append(round_dict[level+1].pop())
                while len(candidates)>0:
                    logging.info(candidates)
                    is_leaf = False
                    m.put()
                    build_matches_helper(m, is_odd, level+1, round+1)
                    i = candidates.pop()
                    logging.info('remove: %d', i)
                    if round_dict.has_key(level+1) and is_odd:
                        if len(candidates)==0 and len(seeded_list)>0:
                            is_odd = False
                            write_player(seeded_list,m)

            if is_leaf:

                write_player(seeded_list,m)
                write_player(seeded_list,m)


        is_odd = False
        if len(seeded_list)%2 == 1:
            is_odd = True
        build_matches_helper(None, is_odd)
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


def get_datatables_records(request, *args):

    cols = int(request.args.get('iColumns',0)) # Get the number of columns
    iDisplayLength =  min(int(request.args.get('iDisplayLength',10)),100)     #Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
    startRecord = int(request.args.get('iDisplayStart',0)) # Where the data starts from (page)
    endRecord = startRecord + iDisplayLength  # where the data ends (end of page)

    columnIndexNameMap = { 0: 'name', 1 : 'type', 2: 'date', 3:'location', 4:'owner', 5:'created', 6:'actions' }
    keys = columnIndexNameMap.keys()
    keys.sort()
    colitems = [columnIndexNameMap[key] for key in keys]
    sColumns = ",".join(map(str,colitems))

    searchableColumns = []
    iSortingCols =  int(request.args.get('iSortingCols',0))
    # Determine which columns are searchable
    for col in range(0,cols):
        if request.args.get('bSearchable_{0}'.format(col), False) == 'true': searchableColumns.append(columnIndexNameMap[col])

    sortedColName = 'created'
    if iSortingCols:
        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(request.args.get('iSortCol_'+str(sortedColIndex),0))
            if request.args.get('bSortable_{0}'.format(sortedColID), 'false')  == 'true':  # make sure the column is sortable first
                sortedColName = columnIndexNameMap[sortedColID]
                sortingDirection = request.args.get('sSortDir_'+str(sortedColIndex), 'asc')
                if sortingDirection == 'desc':
                    sortedColName = '-'+sortedColName
     
    tournaments = []
    customSearch = request.args.get('sSearch', '').encode('utf-8');
    if customSearch != '':
        # TODO: make better a better query algorithm 
        for searchableColumn in searchableColumns:
            tournaments.extend(models.Tournament.all().filter(searchableColumn+" >=", customSearch).filter(searchableColumn+" <", customSearch+ u"\ufffd").order(searchableColumn).order(sortedColName).fetch(1000))
        
        tournaments = [v for v in {tourney.key().id():tourney for tourney in tournaments}.itervalues()]
        sort_attribute = sortedColName.split('-')
        tournaments.sort(key=attrgetter(sort_attribute.pop()), reverse=(len(sort_attribute) == 1))

    else:
        tournaments = models.Tournament.all().order(sortedColName).fetch(3000)

    iTotalRecords = iTotalDisplayRecords = len(tournaments) #count how many records match the final criteria
    tournaments = tournaments[startRecord:endRecord] #get the slice
    sEcho = int(request.args.get('sEcho',0)) # required echo response

    aaData = [[ tournament.name,
                tournament.type,
                tournament.get_date_formatted(),
                tournament.location,
                tournament.owner.get_display_name(),
                tournament.get_created_formatted(),
                render_template('tournament_actions.html', id = tournament.key().id())] 
                for tournament in tournaments]

    response_dict = {}
    response_dict.update({'aaData':aaData})
    response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords, 'iTotalDisplayRecords':iTotalDisplayRecords, 'sColumns':sColumns})
    response =  json.dumps(response_dict)

    return response

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
