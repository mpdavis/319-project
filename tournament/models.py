from google.appengine.ext import db
from auth import models as auth_models
import actions
import json


class Tournament(db.Model):
    """
    Children: Matches
    """
    name = db.StringProperty()
    date = db.DateTimeProperty()
    location = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    owner = db.ReferenceProperty(auth_models.WTUser)
    admins = db.ListProperty(db.Key)

    #PERMISSON CONSTANTS
    PUBLIC = 'public'
    PROTECTED = 'protected'
    PRIVATE = 'private'
    PERMISSION_CHOICES = [PUBLIC,PROTECTED,PRIVATE]
    perms = db.StringProperty(choices=PERMISSION_CHOICES)

    #TYPE CONSTANTS
    SINGLE_ELIMINATION = 'SE'
    DOUBLE_ELIMINATION = 'DE'
    ROUND_ROBIN = 'RR'
    TOURNAMENT_TYPES = [SINGLE_ELIMINATION,
                        DOUBLE_ELIMINATION,
                        ROUND_ROBIN]
    type = db.StringProperty(choices=TOURNAMENT_TYPES)

    order = db.IntegerProperty()
    next_tournament = db.SelfReferenceProperty()
    #Win Methods
    win_method = db.IntegerProperty()
    HIGHEST_WINS = 0
    LOWEST_WINS = 1

    def get_type_verbose(self):
        TYPE_DICT = {
            'SE': "Single Elimination",
            'DE': "Double Elimination",
            'RR': "Round Robin"
        }
        return TYPE_DICT.get(self.type)

    def get_date_formatted(self):
        if self.date:
            return self.date.strftime("%m/%d/%y %I:%M %p")
        return ''

    def get_created_formatted(self):
        if self.created:
            return self.created.strftime("%m/%d/%y %I:%M %p")
        return ''

    def keystr(self):
        return str(self.key())


class Match(db.Model):
    """
    Parent: Tournament
    Children: Participants
    """
    round = db.IntegerProperty()
    status = db.IntegerProperty()
    next_match = db.SelfReferenceProperty()

    NOT_STARTED_STATUS = -1
    IN_PROGRESS_STATUS = 0
    FINISHED_STATUS = 1

    #Fields for Single Elimination
    first_match = db.SelfReferenceProperty(collection_name="first_match_reference_set")
    second_match = db.SelfReferenceProperty(collection_name="second_match_reference_set")

    def add_children_match(self, match):
        if not self.first_match:
            self.first_match = match
            self.put()
        elif not self.second_match:
            self.second_match = match
            self.put()
        else:
            raise Exception("There were more than 2 children matches returned for this match.  " +
                            "Something is wrong.")

    def is_leaf(self):
        return not self.first_match and not self.second_match

    def get_children_matches(self):
        matches = []
        if self.first_match:
            matches.append(self.first_match)
        if self.second_match:
            matches.append(self.second_match)
        return matches


    def determine_winner(self):
        if self.status != self.FINISHED_STATUS:
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

class MatchEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Match):
            winner = "?"
            if obj.status==Match.FINISHED_STATUS:
                winner = obj.determine_winner()
            children = None
            if not obj.is_leaf():
                children = obj.get_children_matches()
            participants = actions.get_participants_by_match(obj)
            users = []
            if len(participants) > 1:
                for i in range(len(participants)):
                    users.append({"name":participants[i].name})
            #id is not stable here for some reason.

            return {"id":obj.key().id(),"winner":winner,"children":children,"participants":users,"status":obj.status}

        else:
            return ""

        return json.JSONEncoder.default(self, obj)


class Participant(db.Model):
    """
    Parent: Match
    """
    seed = db.IntegerProperty()
    user = db.ReferenceProperty(auth_models.WTUser)
    name = db.StringProperty()
    score = db.FloatProperty(default=0.0)

    def get_participant_name(self):
        if self.user:
            return self.user.get_display_name()
        else:
            return self.name
