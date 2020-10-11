from datetime import datetime
from .. import db

class Sex(db.Model):
    __tablename__ = 'sexes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(1), unique=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='sex', lazy='dynamic')

    @staticmethod
    def insert_sexes():
        sexes = {'M':'Male', 'F':'Female'}
        for sex_key in sexes:
            sex = Sex(code=sex_key, name=sexes[sex_key])
            db.session.add(sex)
        db.session.commit()

    def __repr__(self):
        return '<Sex \'%s\'>' % self.name