import os

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

# Config

config = ConfigParser()
config.read([
    os.path.expanduser(os.environ.get('RUGMI_CONF', '~/.rugmi.conf')),
    "/etc/rugmi.conf",
])

# get config
keys = list(map(lambda a: a.strip(), config.get("server", "keys").split(",")))
url = config.get("server", "url").rstrip("/").encode("utf8")
store_path = config.get("server", "store_path").rstrip("/").encode("utf8")
debug = config.getboolean("server", "debug")
