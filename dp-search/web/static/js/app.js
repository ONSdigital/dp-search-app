$(document).ready(function() {
    function getQueryString() {
        return $('input.typeahead.tt-input').val();
    }

    var suggest = new Bloodhound({
      datumTokenizer: function(datum) {
        return Bloodhound.tokenizers.whitespace(datum.value);
      },
      queryTokenizer: function(s) {
        return Bloodhound.tokenizers.whitespace(s)
      },
      rateLimitWait: 500,
      remote: {
        url: '/suggest/autocomplete?q=%QUERY',
        wildcard: '%QUERY',
        filter: function(data) {
            var result = data.suggestions
            var suggestions = []

            // Preserve order of tokens in query
            var query = getQueryString()
            var tokens = Bloodhound.tokenizers.whitespace(query)

            // Log keywords with separate AJAX call
            $.ajax({
                url: "/suggest/keywords?q=" + encodeURI(query),
                type: "GET",
                success: function(data) {
                    console.log("Keywords:")
                    console.log(data)
                }
            });

            tokens.forEach(function(token) {
                if (token in result) {
                    var options = result[token];
                    if (("suggestions" in options) && ($.isArray(options["suggestions"]))
                                && (options["suggestions"].length > 0)) {
                        // Take top result only
                        suggestions.push(options["suggestions"][0].suggestion);
                    } else {
                        suggestions.push(token);
                    }
                } else {
                    suggestions.push(token);
                }
            });

            return {value: suggestions.join(" ")};
        }
      }
    });

    // Initialise the bloodhound engine
    suggest.initialize();

    function updateResults() {
        var query = getQueryString();
        $.ajax({
            url: "/search/ons?q=" + encodeURI(query),
            type: "POST",
            success: function(data) {
                $("ul#search-results").empty()
                $.each(data.hits, function(i, hit) {
                    var li = '<li><a href="#">' + hit.description.title + ' - ' + hit.type + '</a></li>'
                    $("ul#search-results").append(li)
                });
            }
        });
    }

    $('.typeahead').typeahead({
      hint: true,
      highlight: true,
      minLength: 1,
      limit: 20
    },
    {
      name: 'suggest',
      source: suggest.ttAdapter()
    }).on('keyup', this, function(event) {
        if (event.keyCode == 13) {
            updateResults();
        }
    });

    // Add onclick to search button
    $('a.button-search').click(function() {
        updateResults();
    });

    // Add onclick refresh of page
    $('a.navbar-brand').click(function() {
        location.reload();
    });
});

