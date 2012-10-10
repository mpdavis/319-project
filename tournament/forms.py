import wtforms as forms

class NewTournamentStep1(forms.Form):
    SECURITY_CHOICES = [('public', 'Public'),
                        ('protected', 'Protected'),
                        ('private', 'Private')]
    tournament_security = forms.RadioField(choices=SECURITY_CHOICES)

class NewTournamentStep2(forms.Form):
    name = forms.StringField("Name")
    location = forms.StringField("Location", [forms.validators.Optional()])
    date = forms.DateTimeField("Date", [forms.validators.Optional()])
