import re
import itertools
from functools import wraps
from rugmi.plugins.core import NotFoundError, response

class InvalidUrlDefinition(Exception):
    pass

class UrlNotFound(Exception):
    pass

routes = {}

# stolen from werkzeug
_rule_re = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
''', re.VERBOSE)

def flatten(l):
    return list(itertools.chain(*l))

def build_rule(rule):
    rule_re = ""
    match = _rule_re.match
    pos = 0
    end = len(rule)
    while pos < end:
        m = match(rule, pos)
        if m is None:
            break
        pos = m.end()
        data = m.groupdict()
        static = data.get("static", "")
        if static:
            rule_re += static
        variable = data["variable"]
        rule_re += r"(?P<%s>[^/]+)" % re.escape(variable)
    if pos < end:
        rule_re += rule[pos:]
    if not rule_re:
        raise InvalidUrlDefinition
    return "^%s$" % rule_re

def rule_to_url(rule, **kwargs):
    def replace(matchobj):
        static =  matchobj.group(1)
        variable = matchobj.group(2)
        return static + str(kwargs[variable])
    return _rule_re.sub(replace, rule)

def route(rule, methods=["GET"]):
    def decorator(func):
        name = func.__name__
        rule_re = re.compile(build_rule(rule))
        route = dict(rule=rule, rule_re=rule_re, func=func,
                methods=methods)
        routes.setdefault(name, [])
        routes[name].append(route)

        @wraps(func)
        def wrapper(environ, start_response):
            return func(environ, start_response)

        return wrapper
    return decorator

def _url_for(name, **kwargs):
    if not name in routes:
        raise InvalidUrlDefinition
    for route in routes[name]:
        try:
            return rule_to_url(route["rule"], **kwargs)
        except KeyError:
            continue
    raise UrlNotFound

@response
def not_found(environ, start_response):
    raise NotFoundError

# Application

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ["REQUEST_METHOD"]
    for route in flatten(routes.values()):
        if method not in route["methods"]:
            continue
        match = route["rule_re"].match(path)
        if match is not None:
            environ['rugmi.url_args'] = match.groupdict()
            return route["func"](environ, start_response)
    return not_found(environ, start_response)
