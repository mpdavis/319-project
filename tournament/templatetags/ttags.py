from google.appengine.ext.webapp import template

register = template.create_template_register()

@register.simple_tag
def render_hidden_fields(fields):
    return_string = []
    for name,value in fields.items():
        return_string.append('<input type="hidden" name="%s" value="%s" />' % (name, value))
    return '\n'.join(return_string)