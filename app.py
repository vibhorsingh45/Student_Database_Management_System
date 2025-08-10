# Importing necessary modules from Flask
from flask import Flask, render_template, request

# Importing MySQL integration for Flask
from flask_mysqldb import MySQL

# Creating the Flask app instance
app = Flask(__name__)

# Configuring database connection
app.config['MYSQL_HOST'] = 'localhost'          # Host where the MySQL server is running
app.config['MYSQL_USER'] = 'root'               # MySQL username
app.config['MYSQL_PASSWORD'] = 'vibhorgr8'      # MySQL password
app.config['MYSQL_DB'] = 'studentdb2'           # Database name

# Connecting Flask app with MySQL
mysql = MySQL(app)

# Route for the home page, showing the student registration form
@app.route('/')
def form():
    return render_template('form.html')  # Renders the HTML form template

# Route to handle form submission (POST request)
@app.route('/submit', methods=['POST'])
def submit():
    # Retrieving form data from the request
    name = request.form['name']
    age = request.form['age']
    roll = request.form['roll']
    city = request.form['city']
    dob = request.form['dob']
    gender = request.form['gender']

    # Creating cursor to interact with MySQL
    cur = mysql.connection.cursor()

    # Executing the INSERT query with the form data
    cur.execute(
        "INSERT INTO students (name, age, roll, city, dob, gender) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, age, roll, city, dob, gender)
    )

    # Committing changes to the database
    mysql.connection.commit()

    # Closing the cursor
    cur.close()

    # Sending confirmation response to the user
    return 'Student registered successfully!'

# Ensures this script runs the app only if it is the main program
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Running the Flask app on port 5001
