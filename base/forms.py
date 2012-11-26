import wtforms


class BaseForm(wtforms.Form):
    form_error = None

    def set_form_error(self, error):
        self.form_error = error