dp-search-app
==================

### Configuration

To configure the application see the "config_*.py" configuration files. Possible common options are:

| Variable             | Default                 | Description
| -------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------
| HOST                 | '0.0.0.0'               | Host address of the app.
| PORT                 | 5000                    | Port on which to listen for requests. 

### Environment variales

| Environment variable | Default                 | Description
| -------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------
| FLASK_CONFIG         | development             | Specify the configuration to be used. Possible values are 'production', 'development' and 'testing'.
| ELASTICSEARCH_URL    | http://localhost:9200   | URL of Elasticsearch cluster.
| SEARCH_INDEX         | ons*                    | The Elasticsearch index to be queried.

To run the tests use: python manage.py test


### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.
