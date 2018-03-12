#!/usr/bin/env python
import os
from app import app
from gevent.wsgi import WSGIServer


if __name__ == '__main__':
    from gevent.pool import Pool

    pool_size = os.environ.get('POOL_SIZE', 8)
    worker_pool = Pool(pool_size)
    # Start the server
    http_server = WSGIServer(('', 5000), app, spawn=worker_pool)

    try:
        http_server.serve_forever()
    except KeyboardInterrupt: 
        http_server.stop()
