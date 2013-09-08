from rugmi.plugins.routing import _url_for

def url_for(name, **kwargs):
    return _url_for(name, **kwargs)
