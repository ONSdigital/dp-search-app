#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:5000 -k gevent -w 4 --threads 12 --timeout 120 flask_gunicorn:app
