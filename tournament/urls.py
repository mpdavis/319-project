from tournament import views as tournament_views

def setup_urls(app):
    app.add_url_rule('/tournament/new/', view_func=tournament_views.New_Tournament.as_view('new-tourney'))
    app.add_url_rule('/tournament/list/', view_func=tournament_views.Tournament_List.as_view('event-list'))
