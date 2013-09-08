
def templated(func):
    tpl = """
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
          {body}
          </div>
        </div>
      </body>
    </html>"""

    @wraps(func)
    def wrapper(environ, start_response):
        body = func(environ, start_response)
        return tpl.format(body=body).encode("utf8")
    return wrapper
