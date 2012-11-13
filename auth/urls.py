from auth import views as auth_views


def setup_urls(app):
    """URLs for the auth module"""
    app.add_url_rule('/auth/login/', view_func=auth_views.login.as_view('login'))
    app.add_url_rule('/auth/logout/', view_func=auth_views.logout.as_view('logout'))
    app.add_url_rule('/auth/register/', view_func=auth_views.register.as_view('register'))
    app.add_url_rule('/auth/check_username/', view_func=auth_views.check_username.as_view('check_username'))
    app.add_url_rule('/auth/welcome/', view_func=auth_views.welcome.as_view('welcome'))

    app.add_url_rule('/auth/facebook_login', view_func=auth_views.facebook_login.as_view('facebook_login'))
    app.add_url_rule('/auth/facebook_authorized', view_func=auth_views.facebook_authorized.as_view('facebook_authorized'))
