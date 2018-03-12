#!/usr/bin/env python
import os
from app import app
from gevent.wsgi import WSGIServer


if __name__ == '__main__':
    # Start the server
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
