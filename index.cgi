#!/usr/bin/python

import os
import cgi
import hashlib

from string import Template
from ConfigParser import ConfigParser


# Debug
#import cgitb
#cgitb.enable()
#cgitb.enable(display=0, logdir="logs")

config = ConfigParser()
config.read("/etc/rugmi.conf")

# get config
keys = map(lambda a: a.strip(), config.get("server", "keys").split(","))
url = config.get("server", "url")
store_path = config.get("server", "store_path")

def response(string, **kwargs):
    print "Content-Type: text/html"
    print
    print Template(string).substitute(kwargs)

def hash(data):
    string = hashlib.md5(data).digest().encode("base64")[:5]
    string = string.replace("/", "_").replace("+", "-")
    return string

def redirect(location):
    print "Status: 301 Moved",
    print "Location:%s" % location
    print

def unautorized():
    print "Status: 401 Unautorized"
    print
    print "Unautorized Man"

def internal_error(error):
    print "Status: 500"
    print
    print error

def parse_form():
    form = cgi.FieldStorage()
    key = form.getfirst("key", None)
    if key not in keys:
        unautorized()
        return

    if not form.getfirst("file", None):
        internal_error("Needs a file!")
        return
    filefield = form["file"]

    data = filefield.value
    if filefield.done == -1:
        internal_error("upload aborted")
        return

    strhash = hash(data)
    if "." in filefield.filename:
        strhash += "." + filefield.filename.rsplit(".", 1)[1]

    with open(store_path + "/%s" % strhash, "w") as fd:
        fd.write(data)

    response("%s/%s" % (url, strhash))

def index():
    response("""
    <html><body>
      <h1>Rugmi!</h1>
      <form enctype="multipart/form-data" method="post">
          <p>Key: <input name="key" type="input"></p>
          <p>File: <input name='file' type='file'><button type='submit'>Send</button></p>
      </form>
    </body></html>""")

method = os.environ.get("REQUEST_METHOD", "GET")
if method == "POST":
    parse_form()
else:
    index()
