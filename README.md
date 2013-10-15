lanschool\_class\_gen
<https://github.com/korylprince/lanschool_class_gen>

[Lanschool](http://www.lanschool.com/) is a great way to monitor students, but can be it can be a pain for teachers to create class lists. Currently Lanschool only allows you to add a student to a class if they are online. This project is a small web interface where a teacher can create and edit class lists without students needing to be online. The server queries an LDAP server (i.e. Active Directory) to search for students.

#Installation#

The instructions work on Ubuntu. They you should be able to install this on any platform that supports Python with a little know-how.

    sudo apt-get install python-virtualenv python-dev libldap2-dev libsasl2-dev
    cd /opt
    sudo virtualenv lanschool
    sudo chown -R www-data:www-data /opt/lanschool
    sudo -u www-data -i bash
    cd /opt/lanschool
    source bin/activate
    git clone https://github.com/korylprince/lanschool_class_gen.git
    cd lanschool_class_gen
    pip install -r requirements.txt
    pip install gunicorn
    cp .env.example .env
    chmod 600 .env #protect the password
    exit
    sudo cp /opt/lanschool/lanschool_class_gen/upstart_lanschool.conf /etc/init/lanschool.conf


#Configuration#

All configuration for deployment is done in `/opt/lanschool/lanschool_class_gen/.env`.

You must configure `LSGEN_LDAP_URI` and `LSGEN_LDAP_BASE`. Everything else has a somewhat useful default that may or may not work for your setup. (Probably not.) 

It is recommended you set `LSGEN_SECRET`. You can generate a new secret by running:

    python -c 'import os,base64;print base64.b64encode(os.urandom(64))'

All configuration options are listed below:

<table>
    <th><tr><td>Name</td><td>Default</td><td>Description</td></tr></th>
    <tr><td>LDAP_URI</td><td>None</td><td>RFC 4516 LDAP URI. Required.</td></tr>
    <tr><td>LDAP_BASE</td><td>None</td><td>Search Base. Required.</td></tr>
    <tr><td>LDAP_DOMAIN</td><td>None</td><td>Useful for Active Directory. If this is set correctly you can save an LDAP call.</td></tr>
    <tr><td>LDAP_AUTH_FILTER</td><td>'objectCategory=Person'</td><td>LDAP filter to specify login users.</td></tr>
    <tr><td>LDAP_FILTER</td><td>'objectCategory=Person'</td><td>LDAP filter to specify users returned in searches.</td></tr>
    <tr><td>LDAP_USERNAME_ATTR</td><td>'uid'</td><td>LDAP attribute to use for usernames.</td></tr>
    <tr><td>LDAP_NAME_ATTR</td><td>'cn'</td><td>LDAP attribute to use for names (full name).</td></tr>
    <tr><td>LDAP_USERNAME_REGEX</td><td>None</td><td>Regex specifying what searched usernames look like. Can be used to improve search performance as only one attribute will need to be searched instead of two.</td></tr>
    <tr><td>LDAP_TIMEOUT</td><td>5</td><td>The timeout passed to all LDAP calls.</td></tr>
    <tr><td>LDAP_SIZELIMIT</td><td>10</td><td>The size limit passed all LDAP searches. Searches returning more than this many results will be canceled.</td></tr>
    <tr><td>LDAP_BIND_USER</td><td>None</td><td>LDAP bind username. Required if your server doesn't support anonymous binds (most don't).</td></tr>
    <tr><td>LDAP_BIND_PASSWD</td><td>None</td><td>LDAP bind password. Required if your server doesn't support anonymous binds (most don't).</td></tr>
    <tr><td>LDAP_CACERTFILE</td><td>'/etc/ssl/certs/ca-certificates.crt'</td><td>Path to CA Certificates file. Required if using ldaps.</td></tr>
    <tr><td>LOGIN_REGEX</td><td>'^[a-zA-Z0-9\-\._]+$'</td><td>Usernames much match this regex to succeed. Misuse of this option could cause a security breach.</td></tr>
    <tr><td>SEARCH_REGEX</td><td>'^[a-zA-Z0-9\-\._\* ]+$'</td><td>Searches much match this regex to succeed. Misuse of this option could cause a security breach.</td></tr>
    <tr><td>SECRET</td><td>None</td><td>Secret key used by Flask to generate secure sessions. This is autogenerated if not set. Make sure to set this or sessions will become invalid each time the server is restarted.</td></tr>
    <tr><td>DEBUG</td><td>False</td><td>Sets the Flask debug option.</td></tr>
    <tr><td>SCRIPT_NAME</td><td>None</td><td>Not used by the application directly, but used by gunicorn and perhaps other servers to set a root url. (ex: route all requests from /app/view to /view).</td></tr>
</table>

See `/opt/lanschool/lanschool_class_gen/.env` for more help setting configuration options.

#Usage#

Once configured correctly, issue:

    sudo service lanschool start

to start the service. You may view the log file at `/var/log/upstart/lanschool.log`. You may access the server at the IP address and port you specified. I recommend you use a webserver like nginx to proxy requests.

If you have any issues or questions (or want to make it better), email the email address below, or open an issue at: <https://github.com/korylprince/lanschool_class_gen/issues>

#Caveats#

I have tested this code with my server, Active Directory. I tried my best to allow configuration so that any LDAP server may be used, however I can only test it with what I have. If you have issues let me know, and even better, if you have patches, send me a pull request.

#Copyright Information#
Copyright 2013 Kory Prince (korylprince AT gmail DAWT com).

License is BSD.
