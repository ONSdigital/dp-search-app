dp-search-app
==================

### Configuration

To configure the application see the "config_*.py" configuration files. Possible common options are:

| Variable                     | Default                 | Description
| -----------------------------| ----------------------- | ----------------------------------------------------------------------------------------------------
| HOST                         | '0.0.0.0'               | Host address of the app.
| PORT                         | 5000                    | Port on which to listen for requests.
| VECTOR_MODELS_DIR            | 'vector_models/'        | Directory containing pre-trained (unsupervised) word2vec models.
| SUPERVISED_VECTOR_MODELS_DIR | 'supervised_models'     | Directory containing pre-training (supervised) fastText models.

### Environment variales

| Environment variable | Default                 | Description
| -------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------
| FLASK_CONFIG         | development             | Specify the configuration to be used. Possible values are 'production', 'development' and 'testing'.
| ELASTICSEARCH_URL    | http://localhost:9200   | URL of Elasticsearch cluster.
| SEARCH_INDEX         | ons*                    | The Elasticsearch index to be queried.
| MONGO_DB             | local                   | Default db to use in mongoDB.
| FLASK_COMPRESSION    | True                    | Compress responses (True/False)
| FLASK_CORS           | False                   | Enable Cross Origin Resource Sharing (CORS) by default (True/False)
| SEARCH_ONLY          | False                   | Enable search API only (True/False)

There are two options for running the server:
Use ```python manage.py runserver``` to run as a WSGIServer (simple), or  ```./run_gunicorn.sh``` to initialise as a 
gunicorn server (supports multi-processing for multiple workers and threads per worker).

To run the tests use: ```python manage.py test```

To see the swagger spec for all APIs, simply open your browser and navigate to the index page (i.e [http://localhost:5000/](http://localhost:5000/))

### Licence

Copyright ©‎ 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE.md) for details.
