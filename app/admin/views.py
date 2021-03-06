import os
import sys
import secrets
from flask import (
    current_app,
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.admin.forms import (
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    InviteUserForm,
    NewUserForm,
    NewTrackForm
)
from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, Track, Activity
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['TRACK_IMAGE_ALLOWED_EXTENSIONS']

@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = os.environ.get('APP_URL','') + url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token
            #_external=True
            )
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'.format(
            user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'.format(
            user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200

# =========== Track ===========
@admin.route('/new-track', methods=['GET', 'POST'])
@login_required
@admin_required
def new_track():
    """Create a new track."""
    track = None
    form = NewTrackForm()
    if form.validate_on_submit():
        if 'picture_path' not in request.files:
            flash('No picture')
            return redirect(request.url)
        file = request.files['picture_path']
        if file.filename == '':
            flash('File not selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_name, file_extension = os.path.splitext(filename)
            final_filename = secrets.token_hex(16) + file_extension
            file.save(os.path.join(current_app.config['TRACK_UPLOAD_FOLDER'], final_filename))
        track = Track(
            name=form.name.data,
            description=form.description.data,
            distance=form.distance.data,
            active_from=form.active_from.data,
            active_to=form.active_to.data,
            picture_path=final_filename,
            allow_user_multiple_activities=form.allow_user_multiple_activities.data,
            owner=current_user.id,
            created_by=current_user.id)
        db.session.add(track)
        db.session.commit()
        flash('Track {} successfully created'.format(track.name),'form-success')
    if track is not None:
        db.session.refresh(track)
        return render_template('admin/manage_track.html', track=track)
    else:
        return render_template('admin/new_track.html', form=form)

@admin.route('/tracks')
@login_required
@admin_required
def created_tracks():
    """View all created tracks."""
    tracks = Track.query.all()
    return render_template(
        'admin/created_tracks.html', tracks=tracks)

@admin.route('/track-info/<int:track_id>')
@admin.route('/track-info/<int:track_id>/info')
@login_required
@admin_required
def track_info(track_id):
    """View track information."""
    track = Track.query.filter_by(id=track_id).first()
    if track is None:
        abort(404)
    return render_template('admin/manage_track.html', track=track)

@admin.route('/track-delete/<int:track_id>')
@login_required
@admin_required
def delete_track_request(track_id):
    """Request deletion of a track."""
    track = Track.query.filter_by(id=track_id).first()
    if track is None:
        abort(404)
    return render_template('admin/manage_track.html', track=track)

@admin.route('/track-delete/<int:track_id>/_delete')
@login_required
@admin_required
def delete_track(track_id):
    """Delete a track."""
    Activity.query.filter_by(track_id=track_id).delete()
    track = Track.query.filter_by(id=track_id).first()
    db.session.delete(track)
    db.session.commit()
    flash('Successfully deleted track %s.' % track.name, 'success')
    return redirect(url_for('admin.created_tracks'))