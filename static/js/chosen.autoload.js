$(document).ready(function(){
    $("select").each(function(){
        settings = {};
        settings['disable_search'] = true;
        if ($(this).hasClass('searchable')) {
            settings['disable_search'] = false;
        }
        if ($(this).hasClass('deselectable')) {
            settings['allow_single_deselect'] = true;
        }
        $(this).chosen(settings);
    });
});
