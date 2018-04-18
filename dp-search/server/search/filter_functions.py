from content_types import *


def content_type_filter_function(content_type):
    return {
        "filter": {
            "term": {
                "_type": content_type.name
            },
        },
        "weight": content_type.weight
    }


def content_filter_functions():
    """
    Returns filter functions used in a content_query
    :return:
    """
    types = [bulletin, article, article_download, timeseries, compendium_landing_page,
             static_adhoc, dataset_landing_page]

    funcs = []

    for content_type in types:
        funcs.append(content_type_filter_function(content_type))
    return funcs
