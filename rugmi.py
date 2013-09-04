#!/usr/bin/env python

import os
import re
import cgi
import base64
import shutil
import hashlib
import tempfile

from functools import wraps
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

# Config

config = ConfigParser()
config.read([
    os.path.expanduser(os.environ.get('RUGMI_CONF', '~/.rugmi.conf')),
    "/etc/rugmi.conf",
])

# get config
keys = list(map(lambda a: a.strip(), config.get("server", "keys").split(",")))
url = config.get("server", "url").rstrip("/").encode("utf8")
store_path = config.get("server", "store_path").rstrip("/").encode("utf8")
debug = config.getboolean("server", "debug")

# Errors

class UnauthorizedError(Exception):
    pass

class InternalError(Exception):
    pass

class NotFoundError(Exception):
    pass

# Helpers

def errorable(error):
    error_str = b""
    for e in error.args:
        if not isinstance(e, bytes):
            e = e.encode("utf8")
        error_str += b" " + e
    return error_str

def response(func):
    @wraps(func)
    def wrapper(environ, start_response):
        if environ["REQUEST_METHOD"] == "POST":
            if environ.get("wsgi.version", None):
                env = environ.copy()
                env['QUERY_STRING'] = ''
                form = cgi.FieldStorage(
                    fp=env['wsgi.input'],
                    environ=env,
                    keep_blank_values=True
                )
            else:
                form = cgi.FieldStorage()
            environ["rugmi.form"] = form

        try:
            data = func(environ, start_response)
            content_type = "text/html"
            if type(data) is tuple:
                data, content_type = data
            start_response('200 OK', [('Content-Type', content_type)])
        except UnauthorizedError as error:
            start_response('401 Unauthorized',
                    [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Unauthorized, man"
        except InternalError as error:
            start_response('500 Internal Error',
                    [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Error"
        except NotFoundError as error:
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Not Found"
        except Exception as error:
            start_response('500 Internal Error',
                    [('Content-Type', 'text/plain')])
            data = b"Unhandled Error"
            if debug:
                data += b"\n\n"
                data += errorable(error)
        return [data]
    return wrapper

# Responses

@response
def parse_form(environ, start_response):
    form = environ["rugmi.form"]
    key = form.getfirst("key", None)
    if key not in keys:
        raise UnauthorizedError

    if not form.getfirst("file", None):
        raise InternalError(b"Needs a file!")

    filefield = form["file"]

    extension = None
    if "." in filefield.filename:
        extension = filefield.filename.rsplit(".", 1)[1].encode("utf8")
        if not extension.isalpha():
            raise InternalError("Invalid Extension")

    strhash = hashlib.md5()

    temp = tempfile.NamedTemporaryFile(delete=False)
    while True:
        part = filefield.file.read(128)
        if not part:
            break
        strhash.update(part)
        temp.write(part)
    temp.close()

    if filefield.done == -1:
        raise InternalError(b"Upload Aborted")

    filename = base64.b64encode(strhash.digest())[:5]
    filename = filename.replace(b"/", b"_").replace(b"+", b"-")
    if extension:
        filename += b"." + extension

    try:
        path = b"/".join([store_path, filename])
        shutil.move(temp.name, path)
    except IOError as e:
        raise InternalError(b"Error saving: " + errorable(e))

    return b"/".join([url, filename]), "text/plain"

@response
def index(environ, start_response):
    return b"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
      <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css">
      </head>
      <body>
        <div class="container">
          <div class="page-header">
            <h1>Rugmi <small>Your dumpster!</small></h1>
          </div>
          <div class="well">
            <form enctype="multipart/form-data" method="post" role="form">
              <div class="form-group">
                <p>Key: <input class="form-control" name="key" type="input"></p>
                <p>File: <input name='file' type='file'></p>
                <p><button type='submit' class='btn btn-primary'>Send</button></p>
              </div>
            </form>
          </div>
        </div>
      </body>
    </html>"""

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

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == "http":
        from wsgiref.simple_server import make_server
        srv = make_server('localhost', 8000, application)
        srv.serve_forever()
    else:
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(application)
