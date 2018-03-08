import os
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api
import queries
import fields

search_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


def get_client(timeout=1000):
    return Elasticsearch(search_url, timeout=timeout)


def get_search_engine(index, timeout=1000):
    return SearchEngine(using=get_client(timeout=timeout), index=index)


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)

    def content_query(self, search_term):
        sort = {fields.releaseDate.name: {"order": "desc"}}
        return self.query(queries.content_query(search_term)).sort(sort)
