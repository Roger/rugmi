import cgi
from functools import wraps
from rugmi.plugins.core import wsgi_wrappers

class InvalidPathInfo(Exception):
    pass

class PathInfoInEnviron(Exception):
    pass

def fix_path_info(application):
    @wraps(application)
    def wrapper(environ, start_response):
        qs = cgi.parse_qs(environ["QUERY_STRING"])
        #if "PATH_INFO" in environ:
        #    raise PathInfoInEnviron

        environ["PATH_INFO"] = "/"
        if "path" in qs:
            if len(qs["path"]) != 1:
                raise InvalidPathInfo

            environ["PATH_INFO"] = qs["path"][0]
            del qs["path"]
            # rebuild query string without path
            environ["QUERY_STRING"] = "&".join(["%s=%s" % (key, v) \
                    for key, value in qs.items() for v in value])
        return application(environ, start_response)
    return wrapper

wsgi_wrappers.append(fix_path_info)


