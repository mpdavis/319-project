from google.appengine.ext import db

class WTUser(db.Model):
    username = db.StringProperty()
    name = db.StringProperty()
    password = db.StringProperty()
    salt = db.StringProperty()
    method = db.StringProperty()
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now=True)
    facebook_id = db.StringProperty()

    def get_display_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_id(self):
        return self.key().id()

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @classmethod
    def get_user_by_facebook_id(cls, facebook_id):
        return WTUser.all().filter('facebook_id =', facebook_id).get()