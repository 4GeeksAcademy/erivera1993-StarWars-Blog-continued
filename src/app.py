"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
# use package-relative imports
from .utils import APIException, generate_sitemap
from .admin import setup_admin
from .models import db, User, Character, Planet, Favorite
# helper: current user (no auth yet)
def get_current_user():
    # without auth, assume the first user is the current user
    user = User.query.first()
    return user

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

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# -----------------
# People endpoints
# -----------------
@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id: int):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200


# -----------------
# Planets endpoints
# -----------------
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id: int):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


# -----------------
# Users endpoints
# -----------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "No users in the system"}), 404
    favs = Favorite.query.filter_by(user_id=user.id).all()
    return jsonify([f.serialize() for f in favs]), 200


# -----------------
# Favorites endpoints
# -----------------
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id: int):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "No users available"}), 404
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    # check existing
    exists = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if exists:
        return jsonify({"msg": "Favorite already exists"}), 400
    fav = Favorite(user_id=user.id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id: int):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "No users available"}), 404
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    exists = Favorite.query.filter_by(user_id=user.id, character_id=people_id).first()
    if exists:
        return jsonify({"msg": "Favorite already exists"}), 400
    fav = Favorite(user_id=user.id, character_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id: int):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "No users available"}), 404
    fav = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite deleted"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id: int):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "No users available"}), 404
    fav = Favorite.query.filter_by(user_id=user.id, character_id=people_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite deleted"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
