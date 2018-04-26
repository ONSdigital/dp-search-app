import hashlib
from flask import Request


class HashDict(dict):

    hash_fields = ["_ga", "_gid"]

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        # optional processing here
        super(HashDict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                if key in self.hash_fields:
                    self[key] = str(hashlib.sha512(other[key]).hexdigest())
                else:
                    self[key] = other[key]
        for key in kwargs:
            if key in self.hash_fields:
                self[key] = str(hashlib.sha512(kwargs[key]).hexdigest())
            else:
                self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            if key in self.hash_fields:
                self[key] = str(hashlib.sha512(value).hexdigest())
            else:
                self[key] = value
        return self[key]


class Request(Request):
    # Use a regular
    dict_storage_class = HashDict
