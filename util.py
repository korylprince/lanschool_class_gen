from functools import wraps
from werkzeug import secure_filename, escape
from flask import g, session, redirect, url_for
from forms import LoginForm, SearchForm, DeleteForm, ExportForm, ImportForm

def login_required(f):
    "view decorator that redirects nonauthenticated users to index"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username', None) is None:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def create_forms():
    g.login_form = LoginForm()
    g.search_form = SearchForm()
    g.delete_form = DeleteForm()
    g.export_form = ExportForm()
    g.import_form = ImportForm()
    # sets form default to stored filename
    if not g.export_form.filename.data and session.get('filename', None):
        g.export_form.filename.data = session['filename']

def set_filename(filename):
    "gets a secure version of filename, sets it in the session, and returns it."
    filename = escape(secure_filename(filename))
    if filename.lower().endswith('.lsc'):
        filename = filename[:-4]
    session['filename'] = filename
    return filename
