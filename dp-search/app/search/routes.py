from flask import request, render_template
from . import search

@search.route('/')
def index():
    return "Hello, World!"
