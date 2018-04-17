# import pkg_resources
# pkg_resources.require("elasticsearch-dsl>=2.0.0,<3.0.0")

from elasticsearch_dsl import query
import fields


def featured_functions():
    funcs = [{
        "filter": {
            "term": {
                "_type": "product_page"
            }
        }
    }, {
        "filter": {
            "term": {
                "_type": "home_page_census"
            }
        }
    }]
    return funcs


def functions():
    funcs = [{
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
    return funcs


def content_query(search_term, functions=None, **kwargs):
    dis_max = {
        "dis_max": {
            "queries": [{
                "bool": {
                    "should": [{
                        "match": {
                            fields.title_no_dates.name: {
                                "query": search_term,
                                "type": "boolean",
                                "boost": 10.0,
                                "minimum_should_match": "1<-2 3<80% 5<60%"
                            }
                        }
                    }, {
                        "match": {
                            fields.title_no_stem.name: {
                                "query": search_term,
                                "type": "boolean",
                                "boost": 10.0,
                                "minimum_should_match": "1<-2 3<80% 5<60%"
                            }
                        }
                    }, {
                        "multi_match": {
                            "query": search_term,
                            "fields": [fields.title.field_name_boosted, fields.edition.field_name_boosted],
                            "type": "cross_fields",
                            "minimum_should_match": "3<80% 5<60%"
                        }
                    }]
                }
            }, {
                "multi_match": {
                    "query": search_term,
                    "fields": [fields.summary.name, fields.metaDescription.name],
                    "type": "best_fields",
                    "minimum_should_match": "75%"
                }
            }, {
                "match": {
                    fields.keywords.name: {
                        "query": search_term,
                        "type": "boolean",
                        "operator": "AND"
                    }
                }
            }, {
                "multi_match": {
                    "query": search_term,
                    "fields": [fields.cdid.name, fields.datasetId.name]
                }
            }, {
                "match": {
                    fields.searchBoost.name: {
                        "query": search_term,
                        "type": "boolean",
                        "operator": "AND",
                        "boost": 100.0
                    }
                }
            }]
        }
    }

    if functions is not None:
        return query.Q(
            "function_score", query=dis_max, functions=functions)
    else:
        return query.Q(
            "function_score", query=dis_max
        )


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
