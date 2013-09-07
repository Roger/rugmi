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
