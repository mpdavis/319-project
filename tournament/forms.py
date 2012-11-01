from tournament import models
import wtforms as forms
from wtforms import validators


class NewTournamentStep1(forms.Form):
    SECURITY_CHOICES = [('public', 'Public'),
                        ('protected', 'Protected'),
                        ('private', 'Private')]
    tournament_security = forms.RadioField(choices=SECURITY_CHOICES)


class NewTournamentStep2(forms.Form):
    name = forms.StringField("Name", [validators.Required()])
    location = forms.StringField("Location")
    date = forms.DateTimeField("Date", [validators.Optional()])


class NewTournamentStep3(forms.Form):
    TOURNAMENT_TYPES = [('SE', 'Single Elimination'),
                        ('DE', 'Double Elimination'),
                        ('RR', 'Round Robin'),]
    type = forms.SelectField("Tourney Type", choices=TOURNAMENT_TYPES)
    number_participants = forms.IntegerField("Number of Participants")
    show_seeds = forms.BooleanField("Enter seeds for each participant", default=True)

    def __init__(self, *args, **kwargs):
        super(NewTournamentStep3, self).__init__(*args, **kwargs)
        setattr(self.show_seeds, 'div_attrs', 'id=show-seeds-div')


class EditTournament(forms.Form):
    name = forms.StringField("Name", [validators.Optional()])
    location = forms.StringField("Location", [validators.Optional()])
    date = forms.DateTimeField("Date", [validators.Optional()])

    SECURITY_CHOICES = [('public', 'Public'),
                ('protected', 'Protected'),
                ('private', 'Private')]
    tournament_security = forms.RadioField(choices=SECURITY_CHOICES)


def handle_participant_forms(request_form, num_participants, include_seeds):
    class ParticipantForm(forms.Form):
        pass
    for index in range(num_participants):
        name_field_name = "participant%sname" % index
        name_field = forms.StringField("", validators=[forms.validators.Required()])
        setattr(ParticipantForm, name_field_name, name_field)
        if include_seeds:
            seed_field_name = "participant%sseed" % index
            seed_field = forms.IntegerField("", validators=[forms.validators.Optional()])
            setattr(ParticipantForm, seed_field_name, seed_field)

    p_form = ParticipantForm(formdata=request_form)
    return p_form

