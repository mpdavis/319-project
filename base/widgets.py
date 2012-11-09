import wtforms
from wtforms.widgets.core import HTMLString


class DateTimeInput(wtforms.widgets.TextInput):
    """
    Widget for showing a datepicker in a TextInput.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        date = ''
        time = ''
        values = kwargs.pop('value').split(' ')
        if len(values) > 1:
            date = values[0]
            time = values[1]
        kwargs.update({'class':'input-small',
                       'value':date})
        kwargs2 = {
            'class':'input-small',
            'style':'margin-left:12px;',
            'value':time,
            'placeholder':"HH:MM (24hr)",
        }

        input = '<input %s>' % self.html_params(name=field.name, **kwargs)
        input2 = '<input %s>' % self.html_params(name=field.name, id=field.name + "_time", type='text', **kwargs2)
        js = '<script type="text/javascript">$(function() { $("#%s").datepicker({ }); });</script>' % field.id
        return HTMLString(input + input2 + js)
