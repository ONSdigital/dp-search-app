def _read_secrets():
    """
    Reads the salt from the secrets file
    :return:
    """
    import os
    import json

    if os.path.isfile("./secrets.json"):
        with open("./secrets.json", "r") as f:
            secrets = json.load(f)
        if "salt" in secrets and "substr_index" in secrets:
            salt = secrets["salt"]
            substr_index = secrets["substr_index"]
            if (isinstance(salt, unicode) or isinstance(salt, str)) and isinstance(substr_index, int):
                return salt, int(substr_index)
            else:
                raise Exception("Incorrect type for salt/substr_index: %s/%s" % (type(salt), type(substr_index)))
        raise Exception("Unable to locate salt and/or substr_index in secrets file")
    else:
        raise IOError("Unable to locate secrets.json file")


_salt, _substr_index = _read_secrets()


def get_salt():
    return _salt


def get_substr_index():
    return _substr_index
