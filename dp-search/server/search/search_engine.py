import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api
from elasticsearch_dsl import MultiSearch as MultiSearch_api

import fields
from queries import content_query, type_counts_query
from filter_functions import content_filter_functions
from type_filter import all_filter_funcs

search_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')


def get_client(timeout=1000):
    return Elasticsearch(search_url, timeout=timeout)


def get_search_engine(index, timeout=1000):
    return SearchEngine(using=get_client(timeout=timeout), index=index)


"""
TODO - Implement MultiSearch:
http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=multisearch#multisearch

TODO - Implement sortBy request param.
"""


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)
        self.info = self._using.info()

    def highlight_title(self):
        s = self._clone()
        s = s.highlight(fields.title.name, fragment_size=0, pre_tags=["<strong>"], post_tags=["</strong>"])
        return s

    def content_query(self, search_term, paginator=None, **kwargs):
        s = self._clone()

        function_scores = kwargs.pop("function_scores", content_filter_functions())
        type_filters = kwargs.pop("type_filters", None)

        if paginator is not None:
            from_start = 0 if paginator.current_page <= 1 else (paginator.current_page - 1) * paginator.size

            query = {
                "from": from_start,
                "size": paginator.size,
                "query": content_query(search_term, function_scores=function_scores),
                "aggs": type_counts_query()
            }
        else:
            query = {
                "query": content_query(search_term, function_scores=function_scores),
                "aggs": type_counts_query()
            }

        # Update query from dict
        s.update_from_dict(query)

        if type_filters is not None:
            if hasattr(type_filters, "__iter__") is False:
                type_filters = [type_filters]
            s = s.filter("terms", type=type_filters)

        # Highlight
        s = s.highlight_title()
        return s

    def type_counts_query(self, search_term, **kwargs):
        """
        TODO - Fix bug where docCounts does not match number of items returned by filter
        :param search_term:
        :param kwargs:
        :return:
        """
        type_filters = all_filter_funcs()
        return self.content_query(search_term, type_filters=type_filters)

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
        s = s.highlight_title()
        return s


class MultiSearchEngine(MultiSearch_api):
    def __init__(self, **kwargs):
        super(MultiSearchEngine, self).__init__(**kwargs)