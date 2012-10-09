from google.appengine.ext import db

class WTUser(db.Model):
    username = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    password = db.StringProperty()
    salt = db.StringProperty()
    method = db.StringProperty()
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now=True)

    def get_display_name(self):
        return "% %" % (self.first_name, self.last_name)
