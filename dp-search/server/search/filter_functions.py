def content_filter_functions():
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