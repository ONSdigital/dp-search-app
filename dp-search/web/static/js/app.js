$(document).ready(function() {
    var suggest = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      rateLimitWait: 500,
      remote: {
        url: '/suggest/autocomplete?q=%QUERY',
        wildcard: '%QUERY',
        filter: function(resp) {
            var result = resp.result
            var suggestions = []

//            console.log(result)

            result.forEach(function(val) {
                suggestions.push(val.name)
            });
            return [{"value": suggestions.join(" ")}]
        }
      }
    });

    function update_results(query) {
        $.ajax({
            url: "/search/ons?q=" + encodeURI(query),
            type: "GET",
            success: function(data) {
                $("ul#search-results").empty()
                $.each(data.hits, function(i, hit) {
                    var li = '<li><a href="#">' + hit.description.title + ' - ' + hit.type + '</a></li>'
                    $("ul#search-results").append(li)
                });
            }
        });
    }

    $('.typeahead').typeahead(null, {
      name: 'suggest',
      display: 'value',
      source: suggest
    }).on('keyup', this, function(event) {
        if (event.keyCode == 13) {
            var query = $('input.typeahead.tt-input').val()
            update_results(query)
        }
    });

    // Add onclick to search button
    $('.glyphicon-search').click(function() {
        var val = $('input.typeahead.tt-input').val()
        console.log(val)
    });
});

