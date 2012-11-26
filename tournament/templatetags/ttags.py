from jinja2.ext import  contextfunction, Markup
import wtforms

from lib import csrf


def setup_jinja2_environment(app):
    jenv = app.jinja_env
    jenv.filters.update({
        # Set filters.
        # ...
    })
    jenv.extensions.update({
        # Set Extensions.
#        'csrf_token': CsrfExtension(j.environment),
        })
    jenv.globals.update({
        # Set global variables.
        'render_hidden_fields': render_hidden_fields,
        'render_feild': render_field,
        'render_form': render_form,
        'render_form_errors': render_form_errors,
        'render_csrf_token': render_csrf_token,
#        'csrf_token':csrf_token,
        # ...
    })
    return

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
    if isinstance(field.widget, wtforms.widgets.HiddenInput):
        return '<li id="li_%(name)s" class="hidden">%(widget)s</li>' % {'name': field.name, 'widget': field.widget}

    classes = ['control-group']
    errors = ''
    if field.errors:
        classes.append('error')
        errors = ' '.join(field.errors)
        if errors[-1] == '.':
            errors = errors[:-1]

    # setup the required indicator
    is_required = False
    for validator in field.validators:
        if isinstance(validator, wtforms.validators.Required):
            is_required = True
            break;
    if is_required and field.label:
        required_indicator =  '<span class="required-indicator" title="This Field is Required">*</span>'
    else:
        required_indicator =  '<span class="required-indicator">&nbsp;</span>'

    # setup the label
    if field.label:
        if isinstance(field.widget, wtforms.widgets.CheckboxInput):
            final_label = "%s%s" % ((label or field.label.text), required_indicator)
        else:
            final_label = "%s:%s" % ((label or field.label.text), required_indicator)
    else:
        final_label = ""

    #setup div_attrs
    div_attrs = ''
    if hasattr(field, 'div_attrs'):
        div_attrs = field.div_attrs

    # render the row
    ctx = {
        'name' : field.name,
        'label': final_label,
        'classes': ' '.join(classes),
        'widget': field(),
        'error': errors,
        'div_attrs': div_attrs,
        }

    template='<div class="%(classes)s" %(div_attrs)s><label class="control-label" for="id_%(name)s">%(label)s</label><div class="controls">%(widget)s<span class="help-inline">%(error)s</span></div></div>'
    checkbox_template='<div class="%(classes)s" %(div_attrs)s><div class="controls"><label class="checkbox">%(widget)s%(label)s</label></div></div>'
    radio_template='<div class="%(classes)s" %(div_attrs)s><label class="control-label" for="id_%(name)s">%(label)s</label><div class="controls radio">%(widget)s</div></div>'
    if isinstance(field.widget, wtforms.widgets.CheckboxInput):
        return Markup(checkbox_template % ctx)
    if isinstance(field, wtforms.RadioField) and isinstance(field.widget, wtforms.widgets.ListWidget):
        return Markup(radio_template % ctx)

    return Markup(template % ctx)


@contextfunction
def render_form(context, form, render_csrf=True):
    #helper for determining visible fields
    def get_visible_inputs(form):
        visible_inputs = []
        for field in form.__iter__():
            if not isinstance(field.widget, wtforms.widgets.HiddenInput):
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
    csrf_token = ''

    if render_csrf:
        csrf_token = render_csrf_token(context)

    return Markup('%s%s%s%s' % (errors, legend, get_fields_html(context, form, single_input), csrf_token))


@contextfunction
def render_form_errors(context, form):
    return Markup(render_form_errors_helper(form))

def render_form_errors_helper(form):
    rendered_form_errors = ''
    error_base = "<div class=\"alert alert-error\">%s</div>"

    if form.errors or (hasattr(form, 'form_error') and form.form_error):
        if hasattr(form, 'form_error') and form.form_error:
            rendered_form_errors = error_base % form.form_error
        else:
            rendered_form_errors = error_base % "There were errors with your form submission. Please correct to continue."
    return rendered_form_errors

@contextfunction
def render_csrf_token(context):
    return Markup('<input type="hidden" name="_csrf_token" value="%s" />' % context['csrf_token']())