#!/usr/bin/env python
import os

from gevent import monkey
from gevent.pool import Pool
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
        print check_output(['nosetests',
                            '-v',
                            '-s',
                            '--with-coverage',
                            '--cover-package=server',
                            '--cover-branches',
                            '--cover-erase',
                            '--cover-html',
                            '--cover-html-dir=cover'])

    # Run the test
    test()


def main():
    from server.app import create_app

    # Create the app
    app = create_app()

    # Need to patch sockets to make requests async
    monkey.patch_all()

    host = app.config.get("HOST", "0.0.0.0")
    port = app.config.get("PORT", 5000)

    # Start the server
    pool_size = int(os.environ.get("POOL_SIZE", 10))
    pool = Pool(pool_size)
    http_server = WSGIServer((host, port), app.wsgi_app, spawn=pool)

    # Start server and catch KeyboardInterrupt to allow for graceful shutdown.
    try:
        app.logger.info("Listening on %s:%d" % (host, port))
        print "Startup complete..."
        http_server.serve_forever()
    except KeyboardInterrupt:
        # Close mongoDB connection
        with app.app_context():
            app.logger.info("Closing mongoDB connection")
            app.db.connection.close()
            app.logger.info("Done")
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
