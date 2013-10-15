import re
from config import *
from werkzeug import secure_filename, escape
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms import validators, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed

def SafeFile(message=None):

    def _safe(form, field):
        if field.data != escape(secure_filename(field.data)):
            raise ValidationError(message)

    return _safe

class LoginForm(Form):
    username = StringField('Username', [
        validators.InputRequired("You must enter a username."),
        validators.Regexp(LOGIN_REGEX, message="You must enter a valid username.")],
        description="Username")
    password = PasswordField('Password',
            [validators.InputRequired("You must enter a password.")],
            description="Password")

class SearchForm(Form):
    search = StringField('Search', [
        validators.InputRequired("You must enter a name or username."),
        validators.Regexp(SEARCH_REGEX, message="You must enter a valid name or username.")],
        description="Name or Username")

class DeleteForm(Form):
    username = StringField('Username', [
        validators.InputRequired("You must supply a username.")],
        description="Username")

class ExportForm(Form):
    filename = StringField('Class Name', [
        validators.InputRequired("You must supply a Class Name."),
        SafeFile(message="You must supply a valid Class Name.")],
        description="Class Name")

class ImportForm(Form):
    upload = FileField('Class List', [FileRequired(),
        FileAllowed(['lsc'], 'Only Lanschool Class Files are allowed.')])
