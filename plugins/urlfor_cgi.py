from rugmi.plugins.routing import _url_for
from rugmi.plugins.fix_path_info import fix_path_info

# rugmi: provides: urlfor

def url_for(name, **kwargs):
    return "?path=%s" % _url_for(name, **kwargs)
