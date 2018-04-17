import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api

import fields
from legacy_queries import content_query, type_counts_query, functions

search_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


def get_client(timeout=1000):
    return Elasticsearch(search_url, timeout=timeout)


def get_search_engine(index, timeout=1000):
    return SearchEngine(using=get_client(timeout=timeout), index=index)


"""
TODO - Implement MultiSearch:
http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=multisearch#multisearch
"""


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)
        self.info = self._using.info()

    def legacy_content_query(self, search_term, **kwargs):
        sort = {fields.releaseDate.name: {"order": "desc"}}
        query = content_query(search_term, **kwargs)
        return self.query(query).sort(sort)

    def type_counts_content_query(self, search_term, **kwargs):
        query = {
            "query": content_query(search_term, filter_functions=functions(), **kwargs),
            "aggs": type_counts_query()
        }
        self.update_from_dict(query)
        return self

    def featured_result_query(self, search_term, **kwargs):
        dis_max = content_query(search_term, **kwargs)
        query = {
            "size": 1,
            "query": dis_max.to_dict()
        }
        self.update_from_dict(query)
        self = self.filter("terms", type=["product_page", "home_page_census"])
        return self
