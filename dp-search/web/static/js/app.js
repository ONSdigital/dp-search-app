$(document).ready(function() {
    var bestPictures = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      rateLimitWait: 500,
      remote: {
        url: '/suggest/autocomplete?q=%QUERY',
        wildcard: '%QUERY',
        filter: function(resp) {
            var result = resp.result
            var suggestions = []

            console.log(result)

            result.forEach(function(val) {
                suggestions.push(val.name)
            });
            return [{"value": suggestions.join(" ")}]
        }
      }
    });

    $('.typeahead').typeahead(null, {
      name: 'best-pictures',
      display: 'value',
      source: bestPictures
    });
});

