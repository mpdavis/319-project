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
    logging.warning(e)
    e.put()
    t = models.Tournament(
        type=f.get('type'),
        order=0,
        win_method=models.Tournament.HIGHEST_WINS,
        parent=e)
    t.put()
    logging.warning(t)

    #TODO: Determine Math objects and coresponding participant objects based on seeds.

