from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField, FileField, TextAreaField, BooleanField
from wtforms.fields.html5 import EmailField, IntegerField, DateField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, Optional
from app import db
from app.models import Role, User, Track
from datetime import date, timedelta

class ChangeUserEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(FlaskForm):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(FlaskForm):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
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
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')

class NewTrackForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 2000)])
    distance = IntegerField('Distance [m]', validators=[InputRequired(), NumberRange(min=10, max=50000)])
    active_from = DateField('Active from', validators=[InputRequired()], format='%Y-%m-%d', default=date.today())
    active_to = DateField('Active to', validators=[InputRequired()], format='%Y-%m-%d', default=date.today() + timedelta(days=30))
    picture_path = FileField('Track picture', validators=[InputRequired()])
    allow_user_multiple_activities = BooleanField('Allow user\'s multiple activities', default=False)
    submit = SubmitField('Add new track')

    def validate_name(self, field):
        if Track.query.filter_by(name=field.data).first():
            raise ValidationError('Track with the name already exists.')

    def validate_active_to(self, field):
        if field.data < self.active_from.data:
            raise ValidationError('"Active to" date must not be earlier than "Active from" date.')