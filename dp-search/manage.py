#!/usr/bin/env python
import os
from gevent.wsgi import WSGIServer
from gevent import monkey


def test():
    from subprocess import call

    os.environ['FLASK_CONFIG'] = 'testing'
    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=server', '--cover-branches',
          '--cover-erase', '--cover-html', '--cover-html-dir=cover'])


def main():
    from server import app

    # Need to patch sockets to make requests async
    monkey.patch_all()

    host = app.config.get("HOST", "0.0.0.0")
    port = app.config.get("PORT", 5000)

    # Start the server
    http_server = WSGIServer((host, port), app)

    # Start server and catch KeyboardInterrupt to allow for graceful shutdown.
    try:
        app.logger.info("Starting server. Address is %s:%d" % (host, port))
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.stop()


def usage(argv):
    print "Usage: python %s <runserver|test>" % argv[0]


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        main()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        usage(sys.argv)
