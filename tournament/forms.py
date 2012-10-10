import wtforms as forms

class NewTournamentStep1(forms.Form):
    SECURITY_CHOICES = [('public', 'Public'),
                        ('protected', 'Protected'),
                        ('private', 'Private')]
    tournament_security = forms.RadioField(choices=SECURITY_CHOICES)