from google.appengine.ext import db
from auth import models as auth_models


class Event(db.Model):
    """
    Children: Tournaments
    """
    name = db.StringProperty()
    date = db.DateTimeProperty()
    location = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    owner = db.ReferenceProperty(auth_models.WTUser)
    admins = db.ListProperty(db.Key)
    PERMISSION_CHOICES = ['public','protected','private']
    perms = db.StringProperty(choices=PERMISSION_CHOICES)


class Tournament(db.Model):
    """
    Parent: Event
    Children: Matches
    """
    TOURNAMENT_TYPES = ['SE','DE','RR']
    type = db.StringProperty(choices=TOURNAMENT_TYPES)

    order = db.IntegerProperty()
    next_tournament = db.SelfReferenceProperty()

    #Win Methods
    win_method = db.IntegerProperty()
    HIGHEST_WINS = 0
    LOWEST_WINS = 1

    def get_type_verbose(self):
        results = [item[1] for item in self.TOURNAMENT_TYPES if item[0] == self.type]
        return ''.join(results)


class Match(db.Model):
    """
    Parent: Tournament
    Children: Participants
    """
    round = db.IntegerProperty()
    has_been_played = db.BooleanProperty()
    next_match = db.SelfReferenceProperty()

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
    """
    Parent: Match
    """
    seed = db.IntegerProperty()
    user = db.ReferenceProperty(auth_models.WTUser)
    name = db.StringProperty()

    event_key = db.Key()

    def get_participant_name(self):
        if self.user:
            return self.user.get_display_name()
        else:
            return self.name
