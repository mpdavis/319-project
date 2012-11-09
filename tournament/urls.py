from tournament import views as tournament_views

def setup_urls(app):
    app.add_url_rule('/tournament/new/', view_func=tournament_views.New_Tournament.as_view('new-tourney'))
    app.add_url_rule('/tournament/list/', view_func=tournament_views.Tournament_List.as_view('event-list'))
    app.add_url_rule('/tournament/edit/', view_func=tournament_views.Tournament_Edit.as_view('event-edit'))
    app.add_url_rule('/tournament/view/', view_func=tournament_views.Tournament_View.as_view('view-tourney'))
    app.add_url_rule('/tournament/check_email/', view_func=tournament_views.check_email.as_view('check-email'))
