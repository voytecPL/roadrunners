from datetime import datetime
from .. import db

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.String(2000), nullable=True)
    distance = db.Column(db.Integer, nullable=False)
    active_from = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    active_to = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    picture_path = db.Column(db.String(200), unique=True, nullable=False)
    allow_user_multiple_activities = db.Column(db.Boolean, nullable=False, default=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    activities = db.relationship('Activity', backref='track', lazy='dynamic')

    def formatted_name(self):
        if self.distance <= 1000:
            return "{0} - {1} [m]".format(self.name, self.distance)
        else:
            return "{0} - {1} [km]".format(self.name, float(self.distance/1000))

    def formatted_date(self, input_date):
        return input_date.strftime("%Y-%m-%d")