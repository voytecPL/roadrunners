import os
from datetime import datetime, date, timedelta
import tcxparser
from flask import current_app
from .. import db

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(2000), nullable=True)
    start_time_local = db.Column(db.DateTime(), nullable=False, default=date.today)
    start_time_utc = db.Column(db.DateTime(), nullable=True)
    distance = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    gps_screen_path = db.Column(db.String(200), nullable=True)
    start_latitude = db.Column(db.Float, nullable=True)
    start_longitude = db.Column(db.Float, nullable=True)
    end_latitude = db.Column(db.Float, nullable=True)
    end_longitude = db.Column(db.Float, nullable=True)
    moving_duration = db.Column(db.Float, nullable=True)
    elapsed_duration = db.Column(db.Float, nullable=True)
    elevation_gain = db.Column(db.Float, nullable=True)
    elevation_loss = db.Column(db.Float, nullable=True)
    max_elevation = db.Column(db.Float, nullable=True)
    min_elevation = db.Column(db.Float, nullable=True)
    average_speed = db.Column(db.Float, nullable=True)
    average_moving_Speed = db.Column(db.Float, nullable=True)
    max_speed = db.Column(db.Float, nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    average_hr = db.Column(db.Integer, nullable=True)
    max_hr = db.Column(db.Integer, nullable=True)
    average_run_cadence = db.Column(db.Float, nullable=True)
    max_run_cadence = db.Column(db.Integer, nullable=True)
    ground_contact_time = db.Column(db.Float, nullable=True)
    stride_length = db.Column(db.Float, nullable=True)
    vertical_oscillation = db.Column(db.Float, nullable=True)
    training_effect = db.Column(db.Float, nullable=True)
    max_vertical_speed = db.Column(db.Float, nullable=True)
    min_activity_lap_duration = db.Column(db.Float, nullable=True)
    gpx_file = db.Column(db.LargeBinary(), nullable=True)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

    def formatted_duration(self):
        m, s = divmod(int(self.duration), 60)
        h, m = divmod(m, 60)
        return '{:02d}h {:02d}m {:02d}s'.format(h, m, s)

    def from_tcx_file(self):
        if(self.gpx_file):
            tcx = tcxparser.TCXParser(os.path.join(current_app.config['GPX_UPLOAD_FOLDER'], self.name))
            if tcx:
                self.duration = tcx.duration
                self.distance = tcx.distance
                self.start_latitude = tcx.latitude
                self.start_longitude = tcx.longitude
                self.start_time_utc = datetime.strptime(tcx.started_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                self.calories = tcx.calories
                #self.average_run_cadence = tcx.cadence_avg
                #self.max_run_cadence = tcx.cadence_max
                self.average_hr = tcx.hr_avg
                self.max_hr = tcx.hr_max
                self.max_elevation = tcx.altitude_max
                self.min_elevation = tcx.altitude_min
                self.description = tcx.activity_notes
                #tcx.ascent
                #tcx.descent
                #tcx.pace
                #tcx.completed_at
                #tcx.hr_min
