#!/usr/bin/env python
import os

from gevent import monkey
from gevent.wsgi import WSGIServer


def run_tests():
    from flask_script import Manager
    from server.app import create_app

    # Initialise a manager to test our app
    manager = Manager(create_app)

    # Register the test function
    @manager.command
    def test():
        from subprocess import check_output

        os.environ['FLASK_CONFIG'] = 'testing'
        print check_output(['nosetests', '-v', '-s',
                            '--with-coverage', '--cover-package=server', '--cover-branches',
                            '--cover-erase', '--cover-html', '--cover-html-dir=cover'])

    # Run the test
    test()


def main():
    from server import app
    from flasgger import Swagger
    from flask_mongoengine import MongoEngine

    # Create the app
    app = app.create_app()
    # Init mongoDB connection
    app.db = MongoEngine(app)
    # Init swagger API docs
    swagger = Swagger(app)

    # Need to patch sockets to make requests async
    monkey.patch_all()

    host = app.config.get("HOST", "0.0.0.0")
    port = app.config.get("PORT", 5000)

    # Start the server
    http_server = WSGIServer((host, port), app)

    # Start server and catch KeyboardInterrupt to allow for graceful shutdown.
    try:
        app.logger.info("Listening on %s:%d" % (host, port))
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
        run_tests()
    else:
        usage(sys.argv)
