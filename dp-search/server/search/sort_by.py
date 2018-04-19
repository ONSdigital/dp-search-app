import fields
from enum import Enum


class SortFields(Enum):
    first_letter = 1,
    title = 2,
    relevance = 3,
    release_date = 4,
    release_date_asc = 5


class SortOrder(Enum):
    ASC = "asc",
    DESC = "desc"


sort_by = {
    SortFields.first_letter: [
        (fields.title_first_letter, SortOrder.ASC),
        (fields.title_raw, SortOrder.ASC),
        (fields.releaseDate, SortOrder.ASC)
    ],
    SortFields.title: [
        (fields.title_raw, SortOrder.ASC),
        (fields.releaseDate, SortOrder.DESC)
    ],
    SortFields.relevance: [
        (fields._score, SortOrder.DESC),
        (fields.releaseDate, SortOrder.DESC)
    ],
    SortFields.release_date: [
        (fields.releaseDate, SortOrder.DESC),
        (fields._score, SortOrder.DESC)
    ],
    SortFields.release_date_asc: [
        (fields.releaseDate, SortOrder.ASC),
        (fields._score, SortOrder.DESC)
    ]
}


def query_sort(sort_field):
    from collections import OrderedDict
    assert isinstance(sort_field, SortFields), "sort_field must be instance of SortFields enum"
    d = OrderedDict()

    for field, order in sort_by[sort_field]:
        d[field.name] = {"order": order.value}
    return d