import webapp2
from webapp2_extras import jinja2

from jinja2 import nodes
from jinja2.ext import Extension, contextfunction, Markup


def jinja2_factory(app):
    j = jinja2.Jinja2(app)
    j.environment.filters.update({
        # Set filters.
        # ...
    })
    j.environment.extensions.update({
        # Set Extensions.
#        'csrf_token': CsrfExtension(j.environment),
        })
    j.environment.globals.update({
        # Set global variables.
        'uri_for': webapp2.uri_for,
        'render_hidden_fields': render_hidden_fields,
        'csrf_token':csrf_token,
        # ...
    })
    return j

@contextfunction
def render_hidden_fields(context):
    return_string = []
    if 'fields' in context:
        for name,value in context['fields'].items():
            return_string.append('<input type="hidden" name="%s" value="%s" />' % (name, value))
    return Markup('\n'.join(return_string))

@contextfunction
def csrf_token(context):
    #TODO: Implement?  Not sure if we have CSRF protection yet.
    token = context.csrf_token()
    return Markup("<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='%s' /></div>" % token)