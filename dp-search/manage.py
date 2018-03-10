#!/usr/bin/env python
import os
from app import create_app
from gevent.wsgi import WSGIServer


if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), create_app())
    http_server.serve_forever()
