def _read_salt():
    """
    Reads the salt from the secrets file
    :return:
    """
    import os
    import json

    if os.path.isfile("./secrets.json"):
        with open("./secrets.json", "r") as f:
            secrets = json.load(f)
        return secrets["salt"]
    else:
        raise IOError("Unable to locate secrets.json file")


_SALT = _read_salt()


def get_salt():
    return _SALT
