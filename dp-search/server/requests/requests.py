import types
import hashlib
from flask import Request
from werkzeug.datastructures import ImmutableTypeConversionDict


class ImmutableAnonymousIdDict(ImmutableTypeConversionDict):
    """
    An immutable dict to store request params which ensures that GA IDs are always
    one-way hashed BEFORE being stored.
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
        return str(hashlib.sha512(value).hexdigest())


class Request(Request):
    # Use a regular
    dict_storage_class = ImmutableAnonymousIdDict
