from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper')

    serialize_rules = ('-signups.activity', '-campers.activities')

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity')

    serialize_rules = ('-signups.camper', '-activities.campers')

    # ... rest of the model remains the same

    @validates('name')
    def validate_name(self, key, name):
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string.")
        return name

    @validates('age')
    def validate_age(self, key, age):
        if not isinstance(age, int) or age < 8 or age > 18:
            raise ValueError("Age must be between 8 and 18, inclusive.")
        return age

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    serialize_rules = ('-camper.signups', '-activity.signups')

    # ... rest of the model remains the same

    @validates('time')
    def validate_time(self, key, time):
        if not isinstance(time, int) or time < 0 or time > 23:
            raise ValueError("Time must be an integer between 0 and 23, inclusive.")
        return time

    def __repr__(self):
        return f'<Signup {self.id}>'