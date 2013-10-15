from config import *
import ldap
import re

def Student(search, ignore=[]):
    """
    Return a Student, a list of Students, or None depending
    on the amount of objects returned by the query.
    """
    result = _query(search)

    if not result:
        return None

    stulist = [{
                u'username': x[1][LDAP_USERNAME_ATTR][0], 
                u'name': x[1][LDAP_NAME_ATTR][0]
                } for x in result]

    # take out ignore list
    for x in ignore:
        if x in stulist:
            stulist.remove(x)

    # make sure it's not empty
    if not stulist:
        return None

    return stulist if len(stulist) > 1 else stulist[0]


def _query( search):
    try:
        l = ldap.initialize(LDAP_URI)
    except ldap.LDAPError:
        print 'Unable to connect to LDAP server or ill-formatted URI'
        raise
    try:
        l.simple_bind_s(LDAP_BIND_USER,LDAP_BIND_PASSWD)
    except ldap.INVALID_CREDENTIALS:
        print 'Invalid LDAP bind credentials'
        raise
    except ldap.SERVER_DOWN:
        print 'Unable to connect to LDAP server'
        raise

    if LDAP_USERNAME_REGEX is not None:
        # if username regex is specified, only query on the correct attribute
        # otherwise we must query on both
        if LDAP_USERNAME_REGEX.match(search) is not None:
            strfilter = '(&({search_attr}={search})({filter}))'.format(
                    search_attr=LDAP_USERNAME_ATTR,
                    search=search,
                    filter=LDAP_FILTER)
        else:
            strfilter = '(&({search_attr}={search})({filter}))'.format(
                    search_attr=LDAP_NAME_ATTR,
                    search=search,
                    filter=LDAP_FILTER)
    else:
        strfilter = '(&(|({search_attr}={search})({search_attr2}={search}))({filter}))'.format(
                search_attr=LDAP_USERNAME_ATTR,
                search_attr2=LDAP_NAME_ATTR,
                search=search,
                filter=LDAP_FILTER)

    try:
        result = l.search_ext_s(LDAP_BASE, ldap.SCOPE_SUBTREE, strfilter,
                [LDAP_NAME_ATTR, LDAP_USERNAME_ATTR], timeout=float(LDAP_TIMEOUT),
                sizelimit=LDAP_SIZELIMIT)
    except ldap.OPERATIONS_ERROR:
        print 'Unable to search directory. Check LSGEN_LDAP_BIND_* credentials'
        raise

    return result
