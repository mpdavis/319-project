import models

def get_events_by_user(user):
    events = models.Event.all().filter('owner =', user)
    #TODO: account for the admins who should also be able to see the event in their list.
    return events.fetch(200)
