#!/usr/bin/env python
import os
from server import app
from gevent.wsgi import WSGIServer


if __name__ == '__main__':
    from gevent.pool import Pool

    # Start the server
    http_server = WSGIServer(('', 5000), app)

    # Start server and catch KeyboardInterrupt to allow for graceful shutdown.
    try:
        http_server.serve_forever()
    except KeyboardInterrupt: 
        http_server.stop()
