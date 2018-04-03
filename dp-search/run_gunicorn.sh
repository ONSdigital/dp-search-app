#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:5000 -k gevent -w 2 --threads 12 --timeout 120 wsgi:app