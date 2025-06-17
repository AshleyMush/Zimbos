"""
WTForms definitions for user authentication, settings, and admin group management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, URLField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, NumberRange

class RegistrationForm(FlaskForm):
    """
    Form for new user registration, including email confirmation.
    """
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """
    Form for existing users to log in.
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SettingsForm(FlaskForm):
    """
    Form for users to update their profile settings.
    """
    name = StringField('Name', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Changes')

class GroupForm(FlaskForm):
    """
    Admin form to create or update Group entries.
    """
    name = StringField('Group Name', validators=[DataRequired(), Length(max=120)])
    url = URLField('Group URL', validators=[DataRequired(), URL(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    picture_filename = StringField('Picture Filename', validators=[Optional(), Length(max=255)])
    member_count = IntegerField('Member Count', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Group')


class CSRFProtectForm(FlaskForm):
    """
    Empty form just for CSRF protection in AJAX requests.
    """
    pass