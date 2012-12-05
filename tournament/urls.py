from tournament import views as tournament_views

def setup_urls(app):
    app.add_url_rule('/tournament/new/', view_func=tournament_views.New_Tournament.as_view('new-tourney'))
    app.add_url_rule('/tournament/list/', view_func=tournament_views.Tournament_List.as_view('tournament-list'))
    app.add_url_rule('/tournament/edit/<string:tournament_key>/', view_func=tournament_views.Tournament_Edit.as_view('tournament-edit'))
    app.add_url_rule('/tournament/view/<string:tournament_key>/', view_func=tournament_views.Tournament_View.as_view('view-tourney'))
    app.add_url_rule('/tournament/json/<string:tournament_key>/', view_func=tournament_views.Tournament_Json.as_view('tournament-json'))
    app.add_url_rule('/tournament/check_email/', view_func=tournament_views.check_email.as_view('check-email'))
    app.add_url_rule('/tournament/public/view/<string:tournament_key>/', view_func=tournament_views.PublicTournamentView.as_view('public-view-tourney'))
    app.add_url_rule('/tournament/search/', view_func=tournament_views.Tournament_Search.as_view('tournament-search'))
    app.add_url_rule('/tournament/get/', view_func=tournament_views.get_latest_tournaments.as_view('tournament-get'))
    app.add_url_rule('/tournament/update_match/', view_func=tournament_views.update_match.as_view('match_update'))
    app.add_url_rule('/tournament/delete_tournament/', view_func=tournament_views.delete_tournament.as_view('delete_tournament'))
