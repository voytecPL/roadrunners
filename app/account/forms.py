from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    FileField,
    TextAreaField,
    SelectField
)
from wtforms.fields.html5 import EmailField, IntegerField, DateField, DecimalField, TimeField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, Optional
from app import db
from app.models import User, Sex, Activity, Track
from datetime import date


class LoginForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    sex = QuerySelectField(
        'Sex',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Sex).order_by('id'))
    age = IntegerField('Age', validators=[InputRequired(), NumberRange(min=16, max=100)])
    
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to '
                                  '<a href="{}">log in</a> instead?)'.format(
                                    url_for('account.login')))


class RequestResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class NewActivityForm(FlaskForm):
    #track = SelectField('Track', validators=[InputRequired()])
    track = QuerySelectField(
        'Track',
        validators=[InputRequired()],
        get_label='name',
        #blank_text='Select a track...',
        query_factory=lambda: db.session.query(Track).order_by('id'))
    start_time_local = DateField('Date', validators=[InputRequired()], format='%Y-%m-%d', default=date.today())
    duration_hours = IntegerField('Hours', validators=[InputRequired(), NumberRange(min=0, max=24)], default=0)
    duration_minutes = IntegerField('Minutes', validators=[InputRequired(), NumberRange(min=0, max=59)], default=0)
    duration_seconds = IntegerField('Seconds', validators=[InputRequired(), NumberRange(min=0, max=59)], default=0)
    gpx_file = FileField('TCX file', validators=[Optional()])
    submit = SubmitField('Add new Activity')

    def validate_start_time_local(self, field):
        if field.data > date.today():
            raise ValidationError('"Date" must not be later than today\'s date.')
    
    #def validate_duration_seconds(self, field):
    #    if self.duration_hours.data + self.duration_minutes.data + field.data == 0:
    #        raise ValidationError('Activity duration must be greater than 0')