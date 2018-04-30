import types
import hashlib
from flask import Request
from werkzeug.datastructures import ImmutableTypeConversionDict


class ImmutableAnonymousIdDict(ImmutableTypeConversionDict):
    """
    An immutable dict to store request params which ensures that GA IDs are always
    one-way hashed BEFORE ever being stored.
    """

    hash_fields = ["_ga", "_gid"]

    def __init__(self, *args, **kwargs):
        if args:
            if isinstance(args, tuple):
                for arg in args:
                    if isinstance(arg, types.GeneratorType):
                        for key, value in arg:
                            kwargs[key] = value
        for key in kwargs:
            if key in self.hash_fields:
                kwargs[key] = ImmutableAnonymousIdDict.hash_value(kwargs[key])

        super(ImmutableAnonymousIdDict, self).__init__(**kwargs)

    @staticmethod
    def hash_value(value):
        from ..users import get_salt, get_substr_index

        salt = get_salt()
        substr_index = get_substr_index()
        return str(hashlib.sha512(value[substr_index:] + value[:substr_index] + salt).hexdigest())


class Request(Request):
    # Replace the dict storage with the above ImmutableAnonymousIdDict to force hashing of
    # GA IDs
    dict_storage_class = ImmutableAnonymousIdDict
