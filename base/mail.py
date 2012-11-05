from flask import render_template

from google.appengine.api import mail

def send_email(email, subject, body):

    mail.send_mail(sender="Web Tournament Support <computmaxer@gmail.com>",
                   to=email,
                   subject=subject,
                   body=body
    )

def generate_email_body(template, context=None, **kwargs):
    ctx = {}
    if context:
        ctx.update(context)
    ctx.update(kwargs)

    return render_template(template, **ctx)