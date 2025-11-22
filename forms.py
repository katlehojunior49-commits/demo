from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegistrationForm(FlaskForm):
    """Form used for creating new users with validation."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')],
    )
    full_name = StringField('Full Name', validators=[Length(max=120)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Register')


class UpdateProfileForm(FlaskForm):
    """Form for updating existing user profiles."""

    full_name = StringField('Full Name', validators=[Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Update')


class LoginForm(FlaskForm):
    """Simple login form allowing username or email + password."""

    username_or_email = StringField('Username or Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
