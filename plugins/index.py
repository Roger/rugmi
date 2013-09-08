from rugmi.plugins.routing import route
from rugmi.plugins.urlfor import url_for
from rugmi.plugins.template import templated

@route("/")
@response
@templated
def index(environ, start_response):
    return """
        <form enctype="multipart/form-data" method="post" role="form">
          <div class="form-group">
            <p>Key: <input class="form-control" name="key" type="input"></p>
            <p>File: <input name='file' type='file'></p>
            <p><button type='submit' class='btn btn-primary'>Send</button></p>
          </div>
        </form>"""
