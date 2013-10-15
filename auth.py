from config import *
import ldap

def getDN(username):
    "Return the dn and data for a username if possible"
    try:
        l = ldap.initialize(LDAP_URI)
    except ldap.LDAPError:
        print 'Unable to connect to LDAP server or ill-formatted URI'
        raise
    try:
        l.simple_bind_s(LDAP_BIND_USER, LDAP_BIND_PASSWD)
    except ldap.INVALID_CREDENTIALS:
        print 'Invalid LDAP bind credentials'
        raise
    except ldap.SERVER_DOWN:
        print 'Unable to connect to LDAP server'
        raise

    strfilter = '(&({search_attr}={search})({filter}))'.format(
            search_attr=LDAP_USERNAME_ATTR,
            search=username,
            filter=LDAP_AUTH_FILTER)
    return l.search_st(LDAP_BASE, ldap.SCOPE_SUBTREE, strfilter,
            [LDAP_NAME_ATTR, LDAP_USERNAME_ATTR], timeout=float(LDAP_TIMEOUT))

def login(username, password):
    """
    Attempt to login to LSGEN_LDAP_URI. If LSGEN_LDAP_DOMAIN is specified then
    a login of username@LSGEN_LDAP_DOMAIN will be used. (This works on 
    Active Directory at least.) Otherwise an additional LDAP lookup
    will be required to get the DN. If the login is sucessful and
    the data can be fetched for the user subject to LSGEN_LDAP_AUTH_FILTER,
    then the username and name is returned for the user, otherwise
    None is returned.
    """
    try:
        l = ldap.initialize(LDAP_URI)
    except ldap.LDAPError:
        print 'Unable to connect to LDAP server or ill-formatted URI'
        raise
    if LDAP_DOMAIN:
        strlogin = '{0}@{1}'.format(username, LDAP_DOMAIN)
    else:
        try:
            result = getDN(username)
            if result:
                strlogin = result[0][0] #dn
                # cache data so it won't have to be fetched later
                data = result[0][1][LDAP_USERNAME_ATTR][0], result[0][1][LDAP_NAME_ATTR][0] 
            else:
                print 'Invalid login attempt: ', username
                return
        except ldap.OPERATIONS_ERROR:
            print 'Unable to find DN. Check LSGEN_LDAP_BIND_* credentials'
            raise
        except KeyError:
            print 'LDAP Attribute not returned. Check LSGEN_LDAP_USERNAME and LSGEN_LDAP_NAME.'
            raise

    try:
        l.simple_bind_s(strlogin, password)
    except ldap.INVALID_CREDENTIALS:
        print 'Invalid login attempt: ', username
        return
    except ldap.SERVER_DOWN:
        print 'Unable to connect to LDAP server'
        raise

    if not LDAP_DOMAIN:
        print "Login from: ", username
        # data already cached
        return data

    strfilter = '(&({search_attr}={search})({filter}))'.format(
            search_attr=LDAP_USERNAME_ATTR,
            search=username,
            filter=LDAP_AUTH_FILTER)
    result = l.search_st(LDAP_BASE, ldap.SCOPE_SUBTREE, strfilter,
            [LDAP_NAME_ATTR, LDAP_USERNAME_ATTR], timeout=float(LDAP_TIMEOUT))

    if result:
        print "Login from: ", username
        return result[0][1][LDAP_USERNAME_ATTR][0], result[0][1][LDAP_NAME_ATTR][0]
