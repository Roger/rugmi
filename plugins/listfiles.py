from rugmi.plugins.core import response, authenticate
from rugmi.plugins.config import store_path, url
from rugmi.plugins.routing import route
from rugmi.plugins.template import templated

@route("/list/files")
@response
@templated
def indexlist(environ, start_response):
    return """
    <form enctype="multipart/form-data" method="post" role="form">
      <div class="form-group">
        <p>Key: <input class="form-control" name="key" type="input"></p>
        <p><button type='submit' class='btn btn-primary'>Send</button></p>
      </div>
    </form>"""

@route("/list/files", methods=["POST"])
@authenticate
@response
@templated
def listfiles(environ, start_response):
    files = os.listdir(store_path)
    files = (os.path.join(store_path, f) for f in files)
    files = filter(os.path.isfile, files)
    files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    files = map(os.path.basename, files[:20])
    files = map(lambda s: s.decode("utf8"), files)
    return "<br>".join(["<a href='%s/%s'>%s</a>" % (url, f, f) for f in files])
