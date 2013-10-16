import traceback
from ldap import SIZELIMIT_EXCEEDED
from config import *
from util import login_required, create_forms, set_filename
import auth
from student import Student
from flask import Flask, request, g, render_template, redirect, url_for, session, jsonify, make_response
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CsrfProtect
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
app.secret_key = SECRET
app.debug = DEBUG
app.config['BOOTSTRAP_SERVE_LOCAL'] = not USE_CDN

Bootstrap(app)
csrf = CsrfProtect(app)

# add css/js
assets = Environment(app)
js = Bundle('js/main.js', filters='jsmin', output='min/app.js')
assets.register('js_all', js)
css = Bundle('css/main.less', 'css/spinner.less', filters='less,cssmin', output='min/screen.css')
assets.register('css_all', css)

@app.route("/")
def index():
    create_forms()
    if session.get('export_error'):
        g.export_form.filename.errors = session['export_error']
        del session['export_error']
        g.scroll_to = "#export-form-wrapper"
    if session.get('import_error'):
        g.import_form.upload.errors = session['import_error']
        del session['import_error']
        g.scroll_to = "#import-wrapper"
    return render_template('index.html')

@app.route("/login", methods=['POST'])
def login():
    create_forms()
    login_error = None

    if g.login_form.validate_on_submit():
        try:
            user = auth.login(g.login_form.username.data, g.login_form.password.data)
            if user:
                # if ldap data returned, set in session
                session['username'], session['name'] = user
                # send updated view with json
                json = {
                        '#content': render_template('content.html'),
                        '#nav-main': render_template('nav.html')
                        }
                return jsonify(**json)
            else:
                # otherwise it's a bad login
                session.clear()
                # reinitialize csrf
                create_forms()
                login_error = "Invalid Username or Password"
        except:
            # if something goes wrong don't die
            traceback.print_exc()
            login_error = "Server Error. Please try again later"

    # send the updated view with errors
    json = {'#login-wrapper': render_template('login.html', login_error=login_error)}
    return jsonify(**json)

@csrf.exempt # so we don't have to send the csrf token
@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    # reinitialize csrf
    create_forms()

    # return updated view
    json = {
            '#content': render_template('content.html'),
            '#nav-main': render_template('nav.html')
            }
    return jsonify(**json)

@app.route("/add", methods=['POST'])
@login_required
def add():
    create_forms()
    search_error = None
    selection = None

    if g.search_form.validate_on_submit():
        try:
            s = Student(g.search_form.search.data, session.get('students', []))
            if s is None:
                search_error = "No Student(s) found"
            elif isinstance(s, list):
                selection = s                                                                                                                    
                search_error = "Multiple students match search. Please select below"
            else:
                # if single student is returned add to session
                session['students'] = sorted(session.get('students', []) + [s], key=lambda x:x["name"])
                search_error = "{0} ({1}) added to list".format(s['name'], s['username'])
        except SIZELIMIT_EXCEEDED:
            search_error = "Your search returned too many results. Please narrow your search"
        except:
            # if something goes wrong don't die
            traceback.print_exc()
            search_error = "Server Error. Please try again later"

    # keep the same search after clicking selection button
    if request.form.get('original', None):
        g.search_form.search.data = request.form.get('original')

    # send the updated view with errors
    json = {'#content': render_template('content.html', search_error=search_error, selection=selection)}
    return jsonify(**json)

@app.route("/delete", methods=['POST'])
@login_required
def delete():
    create_forms()

    if g.delete_form.validate_on_submit():
        if g.delete_form.username.data == 'all':
            session.pop('students', None)
        else:
            session['students'] = filter(
                    lambda x: x['username'] != g.delete_form.username.data,
                    session.get('students', []))

    # send the updated view with errors
    json = {'#result-wrapper': render_template('result.html', selection=None)}
    return jsonify(**json)

@app.route("/export", methods=['POST'])
@login_required
def export_file():
    create_forms()

    if g.export_form.validate_on_submit():
        # send file
        filename = set_filename(g.export_form.filename.data)
        response = make_response(render_template('list.lsc', session=session))
        response.mimetype = 'application/lsc'
        response.headers['Content-Disposition'] = 'attachment; filename={0}.lsc'.format(filename)
        return response
    else:
        session['export_error'] = g.export_form.filename.errors
        return redirect(url_for('index'))

@app.route("/import", methods=['POST'])
@login_required
def import_file():
    create_forms()
    if g.import_form.validate_on_submit():
        set_filename(request.files['upload'].filename)
        text = request.files['upload'].read()
        s = [Student(x) for x in IMPORT_REGEX.findall(text)]
        s = [x for x in s if isinstance(x, dict)]
        if not s:
            session['import_error'] = ['List did not contain any valid students.']
        else:
            for student in s:
                if student not in session.get('students', []):
                    session['students'] = sorted(session.get('students', []) + [student], key=lambda x:x["name"])

        return redirect(url_for('index'))
    else:
        session['import_error'] = g.import_form.upload.errors
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
