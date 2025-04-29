from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend to communicate with backend

# Database Connection Function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="school_management"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API Endpoint to fetch tables
@app.route('/get_tables', methods=['GET'])
def get_tables():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            return jsonify({"tables": tables})
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)})
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({"error": "Database connection failed"})

if __name__ == '__main__':
    app.run(debug=True)