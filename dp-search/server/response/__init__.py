from flask.json import JSONEncoder


class AutoJSONEncoder(JSONEncoder):
    def default(self, o):
        try:
            return o.__json__()
        except AttributeError:
            return JSONEncoder.default(self, o)
