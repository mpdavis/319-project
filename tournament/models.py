from google.appengine.ext import db
from auth import models as auth_models

class Event(db.Model):
    name = db.StringProperty()
    date = db.DateTimeProperty()
    location = db.StringProperty()

    owner = db.ReferenceProperty(auth_models.WTUser)
    admins = db.ListProperty(db.Key)
    PERMISSION_CHOICES = [('public', 'Public'),
                          ('protected', 'Protected'),
                          ('private', 'Private')]
    perms = db.StringProperty(choices=PERMISSION_CHOICES)


class Tournament(db.Model):
    TOURNAMENT_TYPES = [('RR', 'Round Robin'),
                        ('SE', 'Single Elimination'),
                        ('DE', 'Double Elimination')]
    type = db.StringProperty(choices=TOURNAMENT_TYPES)

    order = db.IntegerProperty()
    next_tournament = db.ReferenceProperty(Tournament)

    #Win Methods
    win_method = db.IntegerProperty()
    HIGHEST_WINS = 0
    LOWEST_WINS = 1


class Match(db.Model):
    round = db.IntegerProperty()
    has_been_played = db.BooleanProperty()
    next_match = db.ReferenceProperty(Match)

    def determine_winner(self):
        if not self.has_been_played:
            return False

        participants = Participant.all().ancestor(self).order('-score')
        if participants.count() == 1:
            return participants[0]
        elif participants.count() == 2:
            return participants[self.parent().win_method]
        elif participants.count() > 2:
            raise Exception("There were more than 2 participants returned for this match.  " +
                            "Something is wrong.")
        else:
            return None


class Participant(db.Model):
    seed = db.IntegerProperty()
    user = db.ReferenceProperty(auth_models.WTUser)
    name = db.StringProperty()

    event_key = db.Key()

    def get_participant_name(self):
        if self.user:
            return self.user.get_display_name()
        else:
            return self.name
