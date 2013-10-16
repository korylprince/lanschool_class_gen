import os, sys
import base64
import re
import traceback
import ldap

def _secret_gen():
    'Generate secret key with a warning'
    secret = base64.b64encode(os.urandom(64))
    print 'Warning: using generated key. Make sure to set LSGEN_SECRET. You can use:'
    print 'LSGEN_SECRET=\'{0}\''.format(secret)
    return secret

def _re_compile(expr):
    'Wrapper for re.compile that will accept None'
    if expr is not None:
        return re.compile(expr)

class RequiredConfigurationException(Exception):
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<RequiredConfigurationException({0})>'.format(self.name)

    def __str__(self):
        return '{0} must be set in the configuration.'.format(self.name)

class ConfigurationErrorException(Exception):
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<ConfigurationErrorException({0})>'.format(self.name)

    def __str__(self):
        return '{0} is misconfigured. (See previouse traceback)'.format(self.name)

def set_env(name, default=None, required=True, post=lambda x:x):
    """
    Helper function to check for environment variables and
    set them up in globals. If default is a callable, then
    name will be set to the return value of default().
    You can optionally set a post function that will 
    be run on the variable. (Useful for setting the type).
    """
    g = globals()
    try:
        g[name] = os.environ.get('LSGEN_'+name, default)
        if g[name] == default and callable(default):
            g[name] = default()
        g[name] = post(g[name])
    except:
        traceback.print_exc()
        print '=' * 50
        raise ConfigurationErrorException(name)
    if g[name] is None and required:
        raise RequiredConfigurationException(name)

set_env('LDAP_URI')
set_env('LDAP_BASE')
set_env('LDAP_DOMAIN', required=False)
set_env('LDAP_AUTH_FILTER', 'objectCategory=Person')
set_env('LDAP_FILTER', 'objectCategory=Person')
set_env('LDAP_USERNAME_ATTR', 'uid')
set_env('LDAP_NAME_ATTR', 'cn')
set_env('LDAP_USERNAME_REGEX', required=False, post=_re_compile)
set_env('LDAP_TIMEOUT', 5, post=int)
set_env('LDAP_SIZELIMIT', 10, post=int)
set_env('LDAP_BIND_USER', '')
set_env('LDAP_BIND_PASSWD', '')
set_env('LDAP_CACERTFILE', '/etc/ssl/certs/ca-certificates.crt', required=False)
set_env('LOGIN_REGEX', '^[a-zA-Z0-9\-\._]+$', post=_re_compile)
set_env('SEARCH_REGEX', '^[a-zA-Z0-9\-\._\* ]+$', post=_re_compile)
set_env('SECRET', default=_secret_gen)
set_env('USE_CDN', True)
set_env('DEBUG', False)

def _initialize():
    ldap.set_option(ldap.OPT_SIZELIMIT, LDAP_SIZELIMIT)

    if LDAP_URI.startswith('ldaps://'):
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, LDAP_CACERTFILE)

    # create import regex from given options
    if LDAP_USERNAME_REGEX:
        regex = LDAP_USERNAME_REGEX.pattern
    else:
        regex = LOGIN_REGEX.pattern

    # strip beginning and ending markers so regex can be
    # inserted into another expression
    if regex.startswith('^'):
        regex = regex[1:]
    if regex.endswith('$'):
        regex = regex[:-1]

    globals()['IMPORT_REGEX'] = re.compile('^Student_[0-9]+=({0})$'.format(regex), re.M)

_initialize()
