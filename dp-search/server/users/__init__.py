import os


def get_salt():
    return os.environ.get("GA_SALT", "")


def get_substr_index():
    return int(os.environ.get("GA_SUBSTR_INDEX", 0))

