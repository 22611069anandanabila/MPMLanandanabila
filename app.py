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
st.set_page_config(page_title="Weather Prediction App", page_icon="🌤️", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_option = st.sidebar.radio("Select a page", ["Enter Data", "View Data"])

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f0f8ff;}
    .title {color: #1e90ff; font-size: 24px; font-weight: bold;}
    .subheader {color: #4682b4; font-size: 20px; font-weight: bold;}
    .button {background-color: #1e90ff; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer;}
    .button:hover {background-color: #4682b4;}
    .dataframe th {background-color: #1e90ff; color: white;}
</style>
""", unsafe_allow_html=True)

if selected_option == "Enter Data":
    st.title("Weather Prediction App")
    st.subheader("Enter New Weather Data")

    # Input fields excluding 'weather'
    date = st.text_input("Date")
    precipitation = st.number_input("Precipitation", format="%.2f")
    temp_max = st.number_input("Max Temperature", format="%.2f")
    temp_min = st.number_input("Min Temperature", format="%.2f")
    wind = st.number_input("Wind", format="%.2f")

    if st.button("Save and Predict", key='save_predict', help="Click to save the data and make a prediction"):
        try:
            # Save the data to the SQLite database
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

elif selected_option == "View Data":
    st.title("Weather Data List")
    con = sql.connect("weather_data.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM weather")
    rows = cur.fetchall()
    con.close()

    # Convert rows to DataFrame for display
    df = pd.DataFrame(rows)
    st.write(df.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#1e90ff'), ('color', 'white')]},
        {'selector': 'tbody td', 'props': [('color', '#333')]},
    ]))
