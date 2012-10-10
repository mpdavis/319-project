import webapp2

from webapp2_extras import jinja2
from jinja2 import nodes
from jinja2.ext import Extension, contextfunction, Markup

import wtforms as forms

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
        'render_feild': render_field,
        'render_form': render_form,
        'render_form_errors': render_form_errors,
#        'csrf_token':csrf_token,
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

#@contextfunction
#def csrf_token(context):
#    #TODO: Implement?  Not sure if we have CSRF protection yet.
#    token = context.csrf_token()
#    return Markup("<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='%s' /></div>" % token)

#Form stuff
@contextfunction
def render_field(context, field, label=None, single_input=False):
    #shortcut for hidden fields
    if isinstance(field.widget, forms.widgets.HiddenInput):
        return '<li id="li_%(name)s" class="hidden">%(widget)s</li>' % {'name': field.name, 'widget': field.widget}

    classes = ['control-group']
    errors = ''
    if field.errors:
        classes.append('error')
        errors = field.errors

    # setup the required indicator
    is_required = True
    for validator in field.validators:
        if isinstance(validator, forms.validators.Optional):
            is_required = False
            break;
    if is_required and field.label:
        required_indicator =  '<span class="required-indicator" title="This Field is Required">*</span>'
    else:
        required_indicator =  '<span class="required-indicator">&nbsp;</span>'

    # setup the label
    if field.label:
        final_label = "%s:%s" % ((label or field.label.text), required_indicator)
    else:
        final_label = ""

    # render the row
    ctx = {
        'name' : field.name,
        'label': final_label,
        'classes': ' '.join(classes),
        'widget': field(),
        'error': errors,
        }

    template='<div class="control-group %(classes)s"><label class="control-label" for="id_%(name)s">%(label)s</label><div class="controls">%(widget)s<span class="help-inline">%(error)s</span></div></div>'
    checkbox_template='<div class="control-group %(classes)s"><label class="checkbox">%(widget)s%(label)s</label></div>'
    if isinstance(field.widget, forms.widgets.CheckboxInput):
        return Markup(checkbox_template % ctx)

    return Markup(template % ctx)


@contextfunction
def render_form(context, form):
    #helper for determining visible fields
    def get_visible_inputs(form):
        visible_inputs = []
        for field in form.__iter__():
            if not isinstance(field.widget, forms.widgets.HiddenInput):
                visible_inputs.append(field)
        return visible_inputs

    # helper for rendering a list of fields
    def get_fields_html(context, form, single_input):
        fields_html = []
        for field in form.__iter__():
            fields_html.append(render_field(context, field, single_input=single_input))
        return ''.join(fields_html)

    errors = render_form_errors_helper(form)
    single_input = len(get_visible_inputs(form)) == 1
    legend = '' #TODO: implement later for form headings.

    return Markup('%s%s%s' % (errors, legend, get_fields_html(context, form, single_input)))


@contextfunction
def render_form_errors(context, form):
    return Markup(render_form_errors_helper(form))

def render_form_errors_helper(form):
    rendered_form_errors = ''
    error_base = "<div class=\"alert alert-error\">There were errors with your form submission. Please correct to continue. %s </div>"

#Looks like WTForms does not have non-field-errors
#    if hasattr(form, 'show_no_base_error'):
#        rendered_form_errors = "<div class=\"error_notice_dialog\">%s</div>" % unicode(form.non_field_errors())
#    elif form.non_field_errors():
#        error_messages = unicode(form.non_field_errors())
#        rendered_form_errors = error_base %  error_messages
    if form.errors:
        rendered_form_errors = error_base % ""
    return rendered_form_errors