from flask import Flask, render_template, request
import joblib
import numpy as np
import sqlite3 as sql

# Initialize Flask application
app = Flask(__name__, template_folder='templates')

# Load the Support Vector Machine model from the file
model = joblib.load('model.sav')
print("Support Vector Machine model successfully loaded")

# Function to create the weather table if it does not exist
def init_db():
    with sql.connect("weather_data.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS weather (
                            date TEXT,
                            precipitation REAL,
                            temp_max REAL,
                            temp_min REAL,
                            wind REAL,
                            weather TEXT
                        )''')
        con.commit()

# Call the init_db function to ensure the table is created when the app starts
init_db()

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route to display the list of weather data
@app.route('/list')
def list_weather():
    con = sql.connect("weather_data.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("SELECT * FROM weather")
    
    rows = cur.fetchall()
    con.close()  # Close the connection after completing
    return render_template("riwayat.html", rows=rows)

# Route for the input form page
@app.route('/enternew')
def new_data():
    return render_template('form_input.html')

# Route to make predictions with the Support Vector Machine model
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get values from the form input
            form_data = request.form.to_dict()
            form_data['date'] = form_data['date']
            form_data['precipitation'] = float(form_data['precipitation'])
            form_data['temp_max'] = float(form_data['temp_max'])
            form_data['temp_min'] = float(form_data['temp_min'])
            form_data['wind'] = float(form_data['wind'])
            form_data['weather'] = form_data['weather']
            
            to_predict_list = [form_data['precipitation'], form_data['temp_max'], form_data['temp_min'], form_data['wind']]

            # Save the data to the SQLite database
            with sql.connect("weather_data.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO weather (date, precipitation, temp_max, temp_min, wind, weather) VALUES (?,?,?,?,?,?)", 
                            (form_data['date'], form_data['precipitation'], form_data['temp_max'], form_data['temp_min'], form_data['wind'], form_data['weather']))
                con.commit()
                msg = "Data successfully saved"

            # Make a prediction with the model
            to_predict = np.array(to_predict_list).reshape(1, -1)  # Use the correct input features for prediction
            result = model.predict(to_predict)[0]

            # Render the template prediction_result.html with the prediction result
            return render_template("prediction_result.html", result=result, msg=msg)
        except Exception as e:
            print(e)
            return "An error occurred during prediction."

if __name__ == '__main__':
    app.run(debug=True, host='192.168.100.76')
