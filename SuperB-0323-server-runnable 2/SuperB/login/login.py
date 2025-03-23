# Author: Zibang Nie, Guanhang Zhang
# This is a Flask application that connects to a MySQL database.
# It contains a single POST route ('/get_user') that retrieves user information
# from the 'Users' table based on a provided name and email.

from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Function to establish a connection to the database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",       # Database host (localhost for local database)
        user="root",            # Database user
        password="1234",        # Database password
        database="booking_system_db"  # The database name to connect to
    )

# Route to get user information based on provided name and email
@app.route('/get_user', methods=['POST'])
def get_user():
    # Get the JSON data from the incoming request
    data = request.get_json()
    email = data.get('email')  # Extract the 'email' value from the JSON data

    # If email is not provided, return an error response
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Query the database to find the user by email
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT role 
        FROM Users 
        WHERE email = %s
    """, (email,))

    user = cursor.fetchone()  # Fetch a single result from the query
    connection.close()  # Close the database connection

    # If a user is found, return the user's role
    if user:
        return jsonify({'role': user['role']})
    else:
        # If no user is found, return an error response
        return jsonify({"error": "User not found"}), 404


# Run the Flask application with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
