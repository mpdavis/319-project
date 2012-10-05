
from google.appengine.api import mail

def send_registration_email(email, username):

    mail.send_mail(sender="Web Tournament Support <computmaxer@gmail.com>",
                   to=email,
                   subject="Welcome to Web Tournaments!",
                   body="""
Hi,

Thanks for signing up for Web Tournaments.

Your username: %s

If you have any problems, contact us at our website and we'll do what we can to help.

We hope you enjoy using Web Tournaments.

Thanks,
The Web Tournament Team
""" % (username))