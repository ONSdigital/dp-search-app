$(document).ready(function() {
    var bestPictures = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/suggest/autocomplete?q=%QUERY',
        wildcard: '%QUERY',
        filter: function(resp) {
            return [resp]
        }
      }
    });

    $('.typeahead').typeahead(null, {
      name: 'best-pictures',
      display: 'value',
      source: bestPictures
    });
});

