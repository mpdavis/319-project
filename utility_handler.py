from google.appengine.ext import webapp

import shell

shell_app = webapp.WSGIApplication(
    [
        ('/shell/', shell.FrontPageHandler),
        ('/shell/shell.do', shell.StatementHandler)
    ], debug=shell._DEBUG)
