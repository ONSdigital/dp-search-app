# import pkg_resources
# pkg_resources.require("elasticsearch-dsl>=2.0.0,<3.0.0")

from elasticsearch_dsl import query
import fields


def content_query(search_term, **kwargs):
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

    # Combine into a bool query if must, should or must_not arguments are given
    if "must" in kwargs or "should" in kwargs or "must_not" in kwargs:
        should = [function_score_query]
        must = []
        must_not = []
        if "must" in kwargs:
            must.extend([content_query(t) for t in kwargs.get("must")])
        if "should" in kwargs:
            should.extend([content_query(t) for t in kwargs.get("should")])
        if "must_not" in kwargs:
            must_not.extend([content_query(t) for t in kwargs.get("must_not")])
        return query.Bool(must=must, should=should, must_not=must_not)

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
