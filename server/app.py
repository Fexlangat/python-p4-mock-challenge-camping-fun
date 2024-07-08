#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Activity, Camper, Signup
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=('-signups', '-activities')) for camper in Camper.query.all()]
        return make_response(jsonify(campers), 200)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(name=data['name'], age=data['age'])
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict(rules=('-signups', '-activities'))), 201)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        return make_response(jsonify(camper.to_dict(rules=('-signups.camper', '-activities'))), 200)

    def patch(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        
        data = request.get_json()
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.commit()
            return make_response(jsonify(camper.to_dict(rules=('-signups', '-activities'))), 202)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=('-signups', '-campers')) for activity in Activity.query.all()]
        return make_response(jsonify(activities), 200)

class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return make_response(jsonify({"error": "Activity not found"}), 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                time=data['time'],
                camper_id=data['camper_id'],
                activity_id=data['activity_id']
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(jsonify(new_signup.to_dict(rules=('-camper.signups', '-activity.signups'))), 201)
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(Campers, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)