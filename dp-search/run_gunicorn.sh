#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:5000 -k gevent -w 8 --threads 32 --timeout 120 flask_gunicorn:app
