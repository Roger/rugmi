from rugmi.plugins.core import NotFoundError, response
from rugmi.plugins.parse_form import parse_form
from rugmi.plugins.index import index

@response
def not_found(environ, start_response):
    raise NotFoundError

# Application

def application(environ, start_response):
    if environ["REQUEST_METHOD"] == "GET":
        return index(environ, start_response)
    elif environ["REQUEST_METHOD"] == "POST":
        return parse_form(environ, start_response)
    return not_found(environ, start_response)
