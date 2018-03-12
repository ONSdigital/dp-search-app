#!/bin/bash

ab -k -n 1000 -c 100 -r http://localhost:5000/search/ons?q=cpi
