import os
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api
from elasticsearch_dsl import aggs

from legacy_queries import content_query, type_counts_query
import fields

search_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


def get_client(timeout=1000):
    return Elasticsearch(search_url, timeout=timeout)


def get_search_engine(index, timeout=1000):
    return SearchEngine(using=get_client(timeout=timeout), index=index)


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)

    def legacy_content_query(self, search_term):
        sort = {fields.releaseDate.name: {"order": "desc"}}
        return self.query(content_query(search_term)).sort(sort)

    def type_counts(self, search_term):
        qb = {
            "query": content_query(search_term).to_dict(),
            "aggs": type_counts_query()
        }
        self.update_from_dict(qb)
        return self
