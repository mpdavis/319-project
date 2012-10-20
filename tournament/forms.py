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
    type = forms.SelectField("Tourney Type", choices=models.Tournament.TOURNAMENT_TYPES)
    number_participants = forms.IntegerField("Number of Participants")
    show_seeds = forms.BooleanField("Enter seeds for each participant", [validators.Optional()], default=True)

    def __init__(self, *args, **kwargs):
        super(NewTournamentStep3, self).__init__(*args, **kwargs)
        setattr(self.show_seeds, 'div_attrs', 'id=show-seeds-div')
