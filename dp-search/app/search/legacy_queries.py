import pkg_resources
pkg_resources.require("elasticsearch-dsl>=2.0.0,<3.0.0")

from elasticsearch_dsl import query
import copy


def content_query(search_term):

    dis_max = {
        "dis_max": {
            "queries": [{
                "bool": {
                    "should": [{
                        "match": {
                            "description.title.title_no_dates": {
                                "query": search_term,
                                "type": "boolean",
                                "boost": 10.0,
                                "minimum_should_match": "1<-2 3<80% 5<60%"
                            }
                        }
                    }, {
                        "match": {
                            "description.title.title_no_stem": {
                                "query": search_term,
                                "type": "boolean",
                                "boost": 10.0,
                                "minimum_should_match": "1<-2 3<80% 5<60%"
                            }
                        }
                    }, {
                        "multi_match": {
                            "query": search_term,
                            "fields": ["description.title^10", "description.edition"],
                            "type": "cross_fields",
                            "minimum_should_match": "3<80% 5<60%"
                        }
                    }]
                }
            }, {
                "multi_match": {
                    "query": search_term,
                    "fields": ["description.summary", "description.metaDescription"],
                    "type": "best_fields",
                    "minimum_should_match": "75%"
                }
            }, {
                "match": {
                    "description.keywords": {
                        "query": search_term,
                        "type": "boolean",
                        "operator": "AND"
                    }
                }
            }, {
                "multi_match": {
                    "query": search_term,
                    "fields": ["description.cdid", "description.datasetId"]
                }
            }, {
                "match": {
                    "searchBoost": {
                        "query": search_term,
                        "type": "boolean",
                        "operator": "AND",
                        "boost": 100.0
                    }
                }
            }]
        }
    }

    functions = [{
        "filter": {
            "term": {
                "_type": "bulletin"
            }
        },
        "weight": 1.55
    }, {
        "filter": {
            "term": {
                "_type": "article"
            }
        },
        "weight": 1.3
    }, {
        "filter": {
            "term": {
                "_type": "article_download"
            }
        },
        "weight": 1.3
    }, {
        "filter": {
            "term": {
                "_type": "timeseries"
            }
        },
        "weight": 1.2
    }, {
        "filter": {
            "term": {
                "_type": "compendium_landing_page"
            }
        },
        "weight": 1.3
    }, {
        "filter": {
            "term": {
                "_type": "static_adhoc"
            }
        },
        "weight": 1.25
    }, {
        "filter": {
            "term": {
                "_type": "dataset_landing_page"
            }
        },
        "weight": 1.35
    }]

    function_score_query = query.Q(
        "function_score", query=dis_max, functions=functions)

    return function_score_query


def type_counts_query():
    type_count_query = {
        "docCounts": {
            "terms": {
                "field": "_type",
                "size": 0
            }
        }
    }

    return type_count_query
