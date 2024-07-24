import streamlit as st
import joblib
import numpy as np
import pandas as pd
import sqlite3 as sql

# Load the Support Vector Machine model from the file
model = joblib.load('model.sav')
st.write("Support Vector Machine model successfully loaded")

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

# Streamlit App
st.title("Weather Prediction App")

# Route for the input form page
st.subheader("Enter New Weather Data")

# Input fields excluding 'weather'
date = st.text_input("Date")
precipitation = st.number_input("Precipitation", format="%.2f")
temp_max = st.number_input("Max Temperature", format="%.2f")
temp_min = st.number_input("Min Temperature", format="%.2f")
wind = st.number_input("Wind", format="%.2f")

if st.button("Save and Predict"):
    try:
        # Save the data to the SQLite database
        # We will set a default value for 'weather' for the storage purpose
        default_weather = "Unknown"
        with sql.connect("weather_data.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO weather (date, precipitation, temp_max, temp_min, wind, weather) VALUES (?,?,?,?,?,?)", 
                        (date, precipitation, temp_max, temp_min, wind, default_weather))
            con.commit()
            st.success("Data successfully saved")

        # Make a prediction with the model
        to_predict_list = [precipitation, temp_max, temp_min, wind]
        to_predict = np.array(to_predict_list).reshape(1, -1)  # Use only the features for prediction
        result = model.predict(to_predict)[0]

        # Display the prediction result
        st.subheader("Prediction Result")
        st.write(f"Predicted Weather: {result}")
        
        # Update the database with the prediction result
        with sql.connect("weather_data.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE weather SET weather = ? WHERE date = ? AND precipitation = ? AND temp_max = ? AND temp_min = ? AND wind = ?",
                        (result, date, precipitation, temp_max, temp_min, wind))
            con.commit()

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Route to display the list of weather data
st.subheader("Weather Data List")
con = sql.connect("weather_data.db")
con.row_factory = sql.Row
cur = con.cursor()
cur.execute("SELECT * FROM weather")
rows = cur.fetchall()
con.close()

# Convert rows to DataFrame for display
df = pd.DataFrame(rows)
st.write(df)
