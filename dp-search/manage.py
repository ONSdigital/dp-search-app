#!/usr/bin/env python
from gevent.wsgi import WSGIServer
from gevent import monkey


def test():
    import os
    from subprocess import call

    os.environ['FLASK_CONFIG'] = 'testing'
    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=server', '--cover-branches',
          '--cover-erase', '--cover-html', '--cover-html-dir=cover'])


def main():
    from server import app

    # need to patch sockets to make requests async
    monkey.patch_all()

    # Start the server
    http_server = WSGIServer(('', 5000), app)

    # Start server and catch KeyboardInterrupt to allow for graceful shutdown.
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.stop()


if __name__ == '__main__':
    import sys

    if sys.argv[1] == "runserver":
        main()
    elif sys.argv[1] == "test":
        test()
    else:
        print "Unknown run option: %s" % sys.argv[1]
