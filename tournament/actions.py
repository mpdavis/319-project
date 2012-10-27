from google.appengine.ext import db

from tournament import models

import logging


def get_events_by_user(user):
    events = models.Event.all().filter('owner =', user).fetch(200)
    #TODO: account for the admins who should also be able to see the event in their list.
    return events


def create_tournament(form_data, p_form_data, user):
    f=form_data
    p=p_form_data
    e = models.Event(
        name=f.get('name'),
        date=f.get('date'),
        location=f.get('location'),
        owner=user,
        perms=f.get('tournament_security'))
    e.put()
    t = models.Tournament(
        type=f.get('type'),
        order=0,
        win_method=models.Tournament.HIGHEST_WINS,
        parent=e)
    t.put()

    name_dict = {}
    seeds = []
    if form_data.get('show_seeds', False):
        raw_seeds = []
        for field, value in p_form_data.items():
            if 'seed' in field:
                num = field[11:-4]
                raw_seeds.append((value, num))
            if 'name' in field:
                num = field[11:-4]
                name_dict[num] = value
        raw_seeds.sort()
        for raw in raw_seeds:
            seeds.append(raw[1])

    else:
        for field, value in p_form_data.items():
            if 'name' in field:
                num = field[11:-4]
                name_dict[num] = value
                seeds.append(num)

    logging.warning(seeds)
    #TODO Optimize puts
    ps_to_put = []
    round = 1
    for i in range(len(seeds)/2):
        m = models.Match(round=round, has_been_played=False, parent=t)
        m.put()
        p1 = models.Participant(seed=int(seeds[i]), name=name_dict.get(seeds[i]), parent=m, event_key=e.key())
        p2 = models.Participant(seed=int(seeds[len(seeds)-i-1]), name=name_dict.get(seeds[len(seeds)-i-1]), parent=m, event_key=e.key())
        ps_to_put.append(p1)
        ps_to_put.append(p2)
        round += 1
    db.put(ps_to_put)
