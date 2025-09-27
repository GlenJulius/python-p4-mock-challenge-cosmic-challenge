#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
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


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        scientists = Scientist.query.all()
        return jsonify([scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in scientists])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study')
            )
            db.session.add(scientist)
            db.session.commit()
            return jsonify(scientist.to_dict()), 201
        except ValueError:
            return jsonify({'errors': ['validation errors']}), 400

@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.get(id)
    
    if not scientist:
        return jsonify({'error': 'Scientist not found'}), 404
    
    if request.method == 'GET':
        return jsonify(scientist.to_dict())
    
    elif request.method == 'PATCH':
        try:
            data = request.get_json()
            if 'name' in data:
                scientist.name = data['name']
            if 'field_of_study' in data:
                scientist.field_of_study = data['field_of_study']
            db.session.commit()
            return jsonify(scientist.to_dict()), 202
        except ValueError:
            return jsonify({'errors': ['validation errors']}), 400
    
    elif request.method == 'DELETE':
        db.session.delete(scientist)
        db.session.commit()
        return jsonify(''), 204

@app.route('/planets', methods=['GET'])
def planets():
    planets = Planet.query.all()
    return jsonify([planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in planets])

@app.route('/missions', methods=['POST'])
def missions():
    try:
        data = request.get_json()
        mission = Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )
        db.session.add(mission)
        db.session.commit()
        return jsonify(mission.to_dict()), 201
    except ValueError:
        return jsonify({'errors': ['validation errors']}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
