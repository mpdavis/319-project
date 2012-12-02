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

def get_json_by_tournament(tournament):
    
    def participants_to_bracket(participants, match_size):
        if len(participants) > match_size and match_size > 1:
            matches = []
            for i in range(len(participants) / match_size):
                matches.append(participants[(i*match_size):((i+1)*match_size)])
            remainder = len(participants) % match_size
            if remainder > 1:
                matches.append(participants[((-1)*remainder):])
            elif remainder > 0:
                if type(participants[-1]) != list:
                    matches.append([participants[-1]])
                else:
                    matches.append(participants[-1])
            matches = participants_to_bracket(matches, match_size)
        else:
            matches = participants
        return matches
    
    def bracket_to_json(bracket):
        assert (type(bracket) == list) and (len(bracket) > 0), \
            "Invalid hierarchal bracket list format."
        json_format = {"winner":"?", "children":[]}
        if type(bracket[0]) == list:
            for i in range(len(bracket)):
                json_format["children"].append(bracket_to_json(bracket[i]))
        else:
            if len(bracket) > 1:
                for i in range(len(bracket)):
                    json_format["children"].append({"name":bracket[i]})
            else:
                json_format = {"name":bracket[0]}
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
    # If odd number of participants, add the middle participant without a pair
    if (len(all_participants) % 2) == 1:
        participant_names.append(
            all_participants[(len(all_participants)/2)].name)
    
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
                seeded_list.append({'name':value,'seed':int(num)+1})  

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
        def rec_build_matches(list_to_use, next_match,level=0):
            def write_player(player, cur_match):
                if player is not None and player['seed'] is not None and player['name'] is not None:
                    p1 = models.Participant(
                        seed=player['seed'],
                        name=player['name'],
                        parent=cur_match)
                    ps_to_put.append(p1)

            num = len(list_to_use)
            if num == 2:
                m = models.Match(round=round_dict[level].pop(), status=models.Match.NOT_STARTED_STATUS, parent=t, next_match = next_match)
                m.put()
                write_player(list_to_use.pop(),m)
                write_player(list_to_use.pop(),m)
            elif num == 1:
                write_player(list_to_use.pop(), next_match)
            elif num > 2:
                left = []
                right = []

                # This is a little complicated, however it splits the seeded people into 
                # left and right branches.  If the player's index is divisble by 4 or their index+1
                # is divisible by 4 they are to be streamed to the right, all the others
                # are streamed left. (notice we go by index and not seed, however seed = index-1)
                # for example 8 seeded tourney (the ones going right are marked)
                # 1 -
                # 2
                # 3
                # 4 -
                # 5 -
                # 6
                # 7
                # 8 -
                # As you can see 1,4,5,8 go on the right side of tournament braket, vise versa 
                # Following the next recursion level...
                # 1 -
                # 4
                # 5
                # 8 -
                # This will sort out the matches with the correct players and 
                # a match tree.

                for i in range(len(list_to_use)):
                    if i%4 == 0 or (i+1)%4 == 0:
                        right.append(list_to_use[i])
                    else:
                        left.append(list_to_use[i])

                m = models.Match(round=round_dict[level].pop(), status=models.Match.NOT_STARTED_STATUS, parent=t, next_match = next_match)
                m.put()

                rec_build_matches(right,m,level+1)
                rec_build_matches(left,m,level+1)

        rec_build_matches(seeded_list,None)

    db.put(ps_to_put)


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