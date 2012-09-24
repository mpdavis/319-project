
import webapp2
from google.appengine.ext.webapp import template

class login(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/login.html', {}))

class logout(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/logout.html', {}))