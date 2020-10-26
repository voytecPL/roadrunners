from flask import Blueprint, render_template, request
from app.models import EditableHTML, Track, Activity
from .. import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    #db.session.query(Activity).order_by('track_id')
    new_activity_id = None
    if(request.args.get('new_activity')):
        new_activity_id = int(request.args.get('new_activity'))
    tracks = Track.query.order_by(Track.id.asc())
    activities = Activity.query.order_by(Activity.track_id.asc(), Activity.duration.asc())
    return render_template('main/index.html', tracks=tracks, activities=activities, new_activity_id=new_activity_id)


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)
