import os

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search as Search_api
from elasticsearch_dsl import MultiSearch as MultiSearch_api

import fields
from search_type import SearchType
from type_filter import all_filter_funcs
from sort_by import SortFields, query_sort
from queries import content_query, type_counts_query
from filter_functions import content_filter_functions
from content_types import home_page_census, product_page

search_url = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')

_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def get_index():
    return _INDEX


def get_client(maxsize=25, timeout=1000):
    """
    :param maxsize: The maximum number of connections that urllib3 can open to each node
    :param timeout:
    :return:
    """
    return Elasticsearch(search_url, timeout=timeout, maxsize=maxsize)


def get_search_engine(index, timeout=1000):
    return SearchEngine(using=get_client(timeout=timeout), index=index)


"""
TODO - Implement MultiSearch:
http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html?highlight=multisearch#multisearch
"""


class SearchEngine(Search_api):

    def __init__(self, **kwargs):
        super(SearchEngine, self).__init__(**kwargs)

    def highlight_fields(self):
        s = self._clone()

        field_names = [field.name for field in fields.highlight_fields]

        s = s.highlight(
            *field_names,
            fragment_size=0,
            pre_tags=["<strong>"],
            post_tags=["</strong>"])

        return s

    @staticmethod
    def build_content_query(search_term, paginator=None, **kwargs):
        function_scores = kwargs.pop(
            "function_scores", content_filter_functions())

        if paginator is not None:
            from_start = 0 if paginator.current_page <= 1 else (
                paginator.current_page - 1) * paginator.size

            query = {
                "from": from_start,
                "size": paginator.size,
                "query": content_query(
                    search_term,
                    function_scores=function_scores).to_dict()}
        else:
            query = {
                "query": content_query(
                    search_term,
                    function_scores=function_scores).to_dict()}
        return query

    def _execute_query(self, query, **kwargs):

        # Clone the SearchEngine before we make changes to it
        s = self._clone()

        # Add type filters?
        type_filters = kwargs.get("type_filters", None)

        # Update query from dict
        s.update_from_dict(query)

        if type_filters is not None:
            if hasattr(type_filters, "__iter__") is False:
                type_filters = [type_filters]
            s = s.filter("terms", type=type_filters)

        # Highlight
        s = s.highlight_fields()

        # Sort
        if "sort_by" in kwargs:
            sort_by = kwargs.pop("sort_by")
            assert isinstance(
                sort_by, SortFields), "sort_by must be instance of SortFields"
            s = s.sort(
                *query_sort(sort_by)
            )

        # DFS_QUERY_THEN_FETCH
        search_type = kwargs.get(
            "search_type",
            SearchType.DFS_QUERY_THEN_FETCH)
        s.search_type(search_type)

        return s

    def content_query(
            self,
            search_term,
            paginator=None,
            **kwargs):
        query = SearchEngine.build_content_query(
            search_term, paginator=paginator, **kwargs)
        return self._execute_query(query, **kwargs)

    def type_counts_query(self, search_term):
        """

        :param search_term:
        :return:
        """
        type_filters = all_filter_funcs()
        query = SearchEngine.build_content_query(search_term)
        query["aggs"] = type_counts_query()

        return self._execute_query(
            query,
            type_filters=type_filters)

    def featured_result_query(self, search_term):
        s = self._clone()
        dis_max = content_query(search_term)
        query = {
            "size": 1,
            "query": dis_max.to_dict()
        }
        # Update query from dict
        s.update_from_dict(query)

        # Add filters
        s = s.filter("terms", type=[product_page.name, home_page_census.name])
        # Add highlights
        s = s.highlight_fields()

        # DFS_QUERY_THEN_FETCH
        s = s.search_type(SearchType.DFS_QUERY_THEN_FETCH)
        return s

    def search_type(self, search_type):
        assert isinstance(
            search_type, SearchType), "Must supply instance of SearchType enum"
        s = self._clone()
        s = s.params(search_type=search_type)

        return s
