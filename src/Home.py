import datetime
import sqlite3
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyModbusTCP.client import ModbusClient
from simple_pid import PID
import streamlit as st

# Modbus connection
host = "192.168.10.200"
client = ModbusClient(host=host, auto_open=True, auto_close=True)
regHeating = 12
regTemperature = 14

# Connect to the SQLite database
conn = sqlite3.connect("temperature.db")
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute(
    """CREATE TABLE IF NOT EXISTS temperature (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperature REAL,
                    timestamp TEXT)"""
)


def read_temperature():
    if temperature := client.read_holding_registers(regTemperature, 1):
        temperature = round(float(temperature[0]) / 10, 1)
        return temperature
    else:
        print("unable to read registers")
        return 33.3


def temp_gauge(temp, previous_temp, gauge_placeholder):
    fig = go.Figure(
        go.Indicator(
            domain={"x": [0, 1], "y": [0, 1]},
            value=temp,
            mode="number+delta",
            title={"text": "Temperature (°C)"},
            delta={"reference": previous_temp},
        )
    )
    gauge_placeholder.write(fig)


def power_gauge(power, previous_power, gauge_placeholder):
    fig = go.Figure(
        go.Indicator(
            domain={"x": [0, 1], "y": [0, 1]},
            value=power,
            mode="gauge+number+delta",
            title={"text": "Power %"},
            delta={"reference": previous_power},
            gauge={"axis": {"range": [0, 100]}},
        )
    )
    gauge_placeholder.write(fig)


def display_chart(temperature_chart):
    df = pd.read_sql_query("SELECT * FROM temperature", conn)
    fig = px.line(df, x="timestamp", y="temperature", title="Temperature History")
    temperature_chart.plotly_chart(fig)


def start_control(setpoint, kp, ki, kd, read_interval):
    pid = PID(kp, ki, kd, setpoint=setpoint, output_limits=(0, 100))
    previous_temp = 0
    previous_power = 0
    gauge_placeholder_temp = st.empty()
    gauge_placeholder_power = st.empty()
    temperature_chart = st.empty()
    while True:
        current_temp = read_temperature()
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Insert the temperature and timestamp into the database
        cursor.execute(
            "INSERT INTO temperature (temperature, timestamp) VALUES (?, ?)",
            (current_temp, timestamp),
        )
        # Commit the changes and close the connection
        conn.commit()
        display_chart(temperature_chart)
        if current_temp is not None:
            controlValue = int(pid(current_temp))
            temp_gauge(current_temp, previous_temp, gauge_placeholder_temp)
            power_gauge(controlValue, previous_power, gauge_placeholder_power)
            previous_temp = current_temp
            controlValue = int(float(controlValue) * 327.67)
            client.write_single_register(regHeating, controlValue)
            # Sleep for the specified interval
            time.sleep(read_interval)


def main():
    st.title("Heating Control App")

    setpoint = st.number_input(
        "Setpoint", min_value=0.0, max_value=40.0, value=24.0, step=0.5
    )
    kp = st.number_input(
        "Proportional Gain (Kp)", min_value=0.0, max_value=50.0, value=15.0, step=0.01
    )
    ki = st.number_input(
        "Integral Gain (Ki)", min_value=0.0, max_value=10.0, value=2.0, step=0.01
    )
    kd = st.number_input(
        "Derivative Gain (Kd)", min_value=0.0, max_value=10.0, value=0.05, step=0.01
    )
    read_interval = st.number_input(
        "Temperature Read Interval (seconds)",
        min_value=1,
        max_value=60,
        value=5,
        step=1,
    )

    col1, col2 = st.columns(2)
    if start_button := col1.button("On / Set Settings"):
        start_control(setpoint, kp, ki, kd, read_interval)

    if stop_button := col2.button("OFF"):
        client.write_single_register(regHeating, 0)
        st.experimental_rerun()


if __name__ == "__main__":
    main()
