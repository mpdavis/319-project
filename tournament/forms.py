from tournament import models
import wtforms as forms
from wtforms import validators

class NewTournamentStep1(forms.Form):
    SECURITY_CHOICES = [('public', 'Public'),
                        ('protected', 'Protected'),
                        ('private', 'Private')]
    tournament_security = forms.RadioField(choices=SECURITY_CHOICES)


class NewTournamentStep2(forms.Form):
    name = forms.StringField("Name")
    location = forms.StringField("Location", [validators.Optional()])
    date = forms.DateTimeField("Date", [validators.Optional()])


class NewTournamentStep3(forms.Form):
    number_participants = forms.IntegerField("Number of Participants")
    type = forms.SelectField("Tourney Type", choices=models.Tournament.TOURNAMENT_TYPES)
