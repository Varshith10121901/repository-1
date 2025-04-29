import mysql.connector
from flask import Flask, render_template, request

app = Flask(__name__)

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "varshith",
}

def create_table():
    """Creates the 'login_peoples' table if it doesn't exist."""
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_peoples (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("Table 'login_peoples' created or already exists.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

create_table()

@app.route("/", methods=["GET", "POST"])
def login():
    """Handles login functionality."""
    message = None  # Initialize message

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM login_peoples WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                message = "Login successful!"
            else:
                message = "Invalid username or password."

            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            message = f"Database error: {err}"

    return render_template("logindatabase.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)