"""
This module takes care of starting the API Server, Loading the DB, and Adding the endpoints.
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# User routes
@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    user = User(email=body["email"], password=body["password"], is_active=body["is_active"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

# Character routes
@app.route('/characters', methods=["GET"])
def get_characters():
    characters = Character.query.all()
    all_characters = list(map(lambda x: x.serialize(), characters))
    return jsonify(all_characters), 200

@app.route('/characters/<int:character_id>', methods=["GET"])
def get_character(character_id):
    character = Character.query.get(character_id)
    return jsonify(character.serialize()), 200

# Planet routes
@app.route('/planets', methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))
    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=["GET"])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    return jsonify(planet.serialize()), 200

# Favorite routes
@app.route('/user/favorites', methods=["GET"])
def get_favorites():
    favorites = Favorite.query.all()
    all_favorites = list(map(lambda x: x.serialize(), favorites))
    return jsonify(all_favorites), 200

@app.route('/favorites/characters/<int:character_id>', methods=["POST"])
def create_favorites_character(character_id):
    body = request.get_json()
    favorite_character = Favorite(user_id=body['user_id'], character_id=character_id)
    db.session.add(favorite_character)
    db.session.commit()
    return jsonify("Character has been added to favorites"), 201

@app.route('/favorites/planets/<int:planet_id>', methods=["POST"])
def create_favorites_planet(planet_id):
    body = request.get_json()
    favorite_planet = Favorite(user_id=body['user_id'], planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()
    return jsonify("Planet has been added to favorites"), 201

# Deletion of favorites
@app.route('/user/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite_user_planet = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_user_planet is None:
        return jsonify("Could not find favorite planet"), 404
    db.session.delete(favorite_user_planet)
    db.session.commit()
    return jsonify("deleted"), 200

@app.route('/user/<int:user_id>/favorites/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    favorite_user_character = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite_user_character is None:
        return jsonify("Could not find favorite character"), 404
    db.session.delete(favorite_user_character)
    db.session.commit()
    return jsonify("deleted"), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
