from google.appengine.ext import db

from base import views as base_views
from flask import render_template
from flask import request
import logging


def setup_urls(app):
    """URLs for the base module"""
    app.add_url_rule('/', view_func=base_views.MainHandler.as_view('home'))
    app.add_url_rule('/about/', view_func=base_views.About.as_view('about'))
    app.add_url_rule('/contact/', view_func=base_views.ContactUs.as_view('contact'))
    app.add_url_rule('/demo/', view_func=base_views.DemoHandler.as_view('demo'))

    @app.errorhandler(404)
    def page_not_found(e):
        logging.error(e)
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        import shell

        session_key = request.args.get('session')
        if session_key:
          session = shell.ShellSession.get(session_key)
        else:
          # create a new session
          session = shell.ShellSession()
          session.unpicklables = [db.Text(line) for line in shell.INITIAL_UNPICKLABLES]
          session_key = session.put()

        ctx = {'shell_session': session_key}
        logging.error(e)
        return render_template('500.html', **ctx), 500
