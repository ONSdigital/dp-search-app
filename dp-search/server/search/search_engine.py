import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api
from elasticsearch_dsl import MultiSearch as MultiSearch_api

import fields
from queries import content_query, type_counts_query
from filter_functions import content_filter_functions

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
        s = self._clone()

        sort = {fields.releaseDate.name: {"order": "desc"}}
        query = content_query(search_term, **kwargs)
        s = s.query(query).sort(sort)
        return s

    def highlight_title(self, search_term):
        s = self._clone()
        s = s.highlight(fields.title.name, fragment_size=0, pre_tags=["<strong>"], post_tags=["</strong>"])
        return s

    def type_counts_content_query(self, search_term, **kwargs):
        s = self._clone()

        function_scores = kwargs.pop("function_scores", content_filter_functions())

        query = {
            "query": content_query(search_term, function_scores=function_scores),
            "aggs": type_counts_query()
        }
        # Update query from dict
        s.update_from_dict(query)

        # Highlight
        s = s.highlight_title(search_term)
        return s

    def featured_result_query(self, search_term, **kwargs):
        s = self._clone()
        dis_max = content_query(search_term)
        query = {
            "size": 1,
            "query": dis_max.to_dict()
        }
        # Update query from dict
        s.update_from_dict(query)

        # Add filters
        s = s.filter("terms", type=["product_page", "home_page_census"])
        # Add highlights
        s = s.highlight_title(search_term)
        return s


class MultiSearchEngine(MultiSearch_api):
    def __init__(self, **kwargs):
        super(MultiSearchEngine, self).__init__(**kwargs)