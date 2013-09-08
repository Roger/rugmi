import base64
import shutil
import hashlib
import tempfile
from rugmi.plugins.core import response, errorable, authenticate
from rugmi.plugins.core import InternalError
from rugmi.plugins.config import keys, store_path, url
from rugmi.plugins.routing import route

@route("/", methods=["POST"])
@authenticate
@response
def parse_form(environ, start_response):
    form = environ["rugmi.form"]

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

