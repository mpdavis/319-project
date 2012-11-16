from tournament import views as tournament_views

def setup_urls(app):
    app.add_url_rule('/tournament/new/', view_func=tournament_views.New_Tournament.as_view('new-tourney'))
    app.add_url_rule('/tournament/list/', view_func=tournament_views.Tournament_List.as_view('tournament-list'))
    app.add_url_rule('/tournament/edit/', view_func=tournament_views.Tournament_Edit.as_view('tournament-edit'))
    app.add_url_rule('/tournament/view/<string:tournament_key>/', view_func=tournament_views.Tournament_View.as_view('view-tourney'))
    app.add_url_rule('/tournament/json/', view_func=tournament_views.Tournament_Json.as_view('tournament-json'))
    app.add_url_rule('/tournament/check_email/', view_func=tournament_views.check_email.as_view('check-email'))

    app.add_url_rule('/tournament/public/view/<string:tournament_key>/', view_func=tournament_views.PublicTournamentView.as_view('public-view-tourney'))
