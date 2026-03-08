# Import Blueprint to create an organized group of routes
from flask import Blueprint, jsonify, request
# Import CORS to allow requests from other domains (frontend)
from flask_cors import CORS
# Import the database models we're going to use
from api.models import db, People, Planets, Users, Favorites

# Create a Blueprint named "api" that groups all API routes
api = Blueprint("api", __name__)
# Enable CORS on all blueprint routes so the frontend can make requests
CORS(api)

# ==================== PEOPLE ENDPOINTS ====================
# Route to get ALL people/characters
@api.route('/people', methods=['GET'])  # Define the '/people' route and accept only GET method
def get_people():  # Function that executes when someone does GET to /people
    people = People.query.all()  # Query the database and fetch ALL records from People table
    # Convert each Person object to JSON using its serialize() method and return a list
    return jsonify([person.serialize() for person in people])

# Route to get ONE specific person by their ID
@api.route('/people/<int:people_id>', methods=['GET'])  # <int:people_id> captures the ID from the URL
def get_person(people_id):  # Receives people_id as parameter
    person = People.query.get(people_id)  # Search the DB for a person with that ID
    if person is None:  # If the person is not found
        return jsonify({"error": "Person not found"}), 404  # Return 404 error (not found)
    return jsonify(person.serialize())  # If found, convert to JSON and return it

# ==================== PLANETS ENDPOINTS ====================
# Route to get ALL planets
@api.route('/planets', methods=['GET'])  # Define the '/planets' route and accept only GET method
def get_planets():  # Function that executes when someone does GET to /planets
    planets = Planets.query.all()  # Query the database and fetch ALL records from Planets table
    # Convert each Planet object to JSON using its serialize() method and return a list
    return jsonify([planet.serialize() for planet in planets])

# Route to get ONE specific planet by its ID
@api.route('/planets/<int:planet_id>', methods=['GET'])  # <int:planet_id> captures the ID from the URL
def get_planet(planet_id):  # Receives planet_id as parameter
    planet = Planets.query.get(planet_id)  # Search the DB for a planet with that ID
    if planet is None:  # If the planet is not found
        return jsonify({"error": "Planet not found"}), 404  # Return 404 error (not found)
    return jsonify(planet.serialize())  # If found, convert to JSON and return it

# ==================== USERS ENDPOINTS ====================
# Route to get ALL users
@api.route('/users', methods=['GET'])  # Define the '/users' route and accept only GET method
def get_users():  # Function that executes when someone does GET to /users
    users = Users.query.all()  # Query the database and fetch ALL records from Users table
    # Convert each User object to JSON using its serialize() method and return a list
    return jsonify([user.serialize() for user in users])

# Route to get all favorites of a specific user
@api.route('/users/favorites', methods=['GET'])  # Define the '/users/favorites' route
def get_user_favorites():  # Function that handles the request
    user_id = request.args.get('user_id')  # Get the user_id from URL parameters (?user_id=123)
    if not user_id:  # If user_id was not provided
        return jsonify({"error": "User ID is required"}), 400  # Return 400 error (bad request)

    # Find all favorites where user_id matches the provided one
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    # Convert each favorite to JSON and return the complete list
    return jsonify([favorite.serialize() for favorite in favorites])

# ==================== FAVORITES ENDPOINTS ====================
# Route to ADD a planet to favorites
@api.route('/favorite/planet/<int:planet_id>', methods=['POST'])  # POST is used to CREATE resources
def add_favorite_planet(planet_id):  # Receives the planet ID from the URL
    user_id = request.json.get('user_id')  # Get the user_id from the JSON request body
    if not user_id:  # If user_id was not sent
        return jsonify({"error": "User ID is required"}), 400  # 400 error

    # Check if the favorite already exists in the database
    existing_favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:  # If it already exists
        return jsonify({"error": "Favorite already exists"}), 400  # Don't allow duplicates

    try:  # Try to create the favorite
        favorite = Favorites(user_id=user_id, planet_id=planet_id)  # Create a new Favorite object
        db.session.add(favorite)  # Add it to the database session
        db.session.commit()  # Save changes to the database
        return jsonify(favorite.serialize()), 201  # Return the created favorite with 201 code (created)
    except Exception as e:  # If something goes wrong
        db.session.rollback()  # Revert changes in the database
        return jsonify({"error": str(e)}), 500  # Return 500 error (server error)

# Route to ADD a person to favorites
@api.route('/favorite/people/<int:people_id>', methods=['POST'])  # POST to create
def add_favorite_people(people_id):  # Receives the person ID from the URL
    user_id = request.json.get('user_id')  # Get the user_id from JSON body
    if not user_id:  # If user_id was not sent
        return jsonify({"error": "User ID is required"}), 400  # 400 error

    # Check if the favorite already exists
    existing_favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if existing_favorite:  # If it already exists
        return jsonify({"error": "Favorite already exists"}), 400  # Don't allow duplicates

    try:  # Try to create the favorite
        favorite = Favorites(user_id=user_id, people_id=people_id)  # Create a new Favorite object
        db.session.add(favorite)  # Add it to the DB session
        db.session.commit()  # Save changes to the DB
        return jsonify(favorite.serialize()), 201  # Return the created favorite with 201 code
    except Exception as e:  # If there's an error
        db.session.rollback()  # Revert changes
        return jsonify({"error": str(e)}), 500  # 500 error

# Route to DELETE a planet from favorites
@api.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])  # DELETE is used to REMOVE resources
def delete_favorite_planet(planet_id):  # Receives the planet ID from the URL
    user_id = request.json.get('user_id')  # Get the user_id from JSON body
    if not user_id:  # If user_id was not sent
        return jsonify({"error": "User ID is required"}), 400  # 400 error

    # Find the specific favorite for user and planet
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:  # If the favorite doesn't exist
        return jsonify({"error": "Favorite not found"}), 404  # 404 error (not found)

    try:  # Try to delete the favorite
        db.session.delete(favorite)  # Mark the favorite for deletion
        db.session.commit()  # Confirm the deletion in the database
        return jsonify({"message": "Favorite planet deleted"}), 200  # Return success message
    except Exception as e:  # If there's an error
        db.session.rollback()  # Revert changes
        return jsonify({"error": str(e)}), 500  # 500 error

# Route to DELETE a person from favorites
@api.route('/favorite/people/<int:people_id>', methods=['DELETE'])  # DELETE to remove
def delete_favorite_people(people_id):  # Receives the person ID from the URL
    user_id = request.json.get('user_id')  # Get the user_id from JSON body
    if not user_id:  # If user_id was not sent
        return jsonify({"error": "User ID is required"}), 400  # 400 error

    # Find the specific favorite for user and person
    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:  # If the favorite doesn't exist
        return jsonify({"error": "Favorite not found"}), 404  # 404 error

    try:  # Try to delete the favorite
        db.session.delete(favorite)  # Mark the favorite for deletion
        db.session.commit()  # Confirm the deletion in the DB
        return jsonify({"message": "Favorite person deleted"}), 200  # Success message
    except Exception as e:  # If there's an error
        db.session.rollback()  # Revert changes
        return jsonify({"error": str(e)}), 500  # 500 error















