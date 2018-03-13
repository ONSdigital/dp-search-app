dp-search-app
==================

### Configuration

| Environment variable | Default                 | Description
| -------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------
| FLASK_CONFIG         | development             | Specify the configuration to be used. Possible values are 'production', 'development' and 'testing'.
| ELASTICSEARCH_URL    | http://localhost:9200   | URL of Elasticsearch cluster.
| SEARCH_INDEX         | ons*                    | The Elasticsearch index to be queried.

To run the tests: python manage.py test


### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.
