import streamlit as st
import pandas as pd
import serial
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import plotly.express as px
import time

# 🔧 SERIAL CONFIG
PORT = 'COM4'
BAUD = 9600

# 🔥 LOAD MODEL + SCALER
model = joblib.load("isolation_model.pkl")
scaler = joblib.load("scaler.pkl")

# 🔥 LOAD DATASET FOR METRICS
df_test = pd.read_csv("well_separated_dataset.csv")

X_test = df_test[['temperature', 'current']]
X_test_scaled = scaler.transform(X_test)

df_test['actual'] = df_test['status'].apply(lambda x: 0 if x == "NORMAL" else 1)

preds = model.predict(X_test_scaled)
df_test['pred'] = [0 if p == 1 else 1 for p in preds]

# 📊 METRICS
accuracy = accuracy_score(df_test['actual'], df_test['pred'])
precision = precision_score(df_test['actual'], df_test['pred'])
recall = recall_score(df_test['actual'], df_test['pred'])
f1 = f1_score(df_test['actual'], df_test['pred'])

# 🔥 SERIAL INIT (FIXED - ONLY ONCE)
if "ser" not in st.session_state:
    try:
        st.session_state.ser = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        st.error(f"❌ Serial port error: {e}")
        st.stop()

ser = st.session_state.ser

# 🎯 UI
st.set_page_config(page_title="AI Dashboard", layout="wide")
st.title("🔥 AI-Based Anomaly Detection Dashboard")

# 📊 MODEL PERFORMANCE
st.subheader("📊 Model Performance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy", f"{accuracy*100:.2f}%")
col2.metric("Precision", f"{precision*100:.2f}%")
col3.metric("Recall", f"{recall*100:.2f}%")
col4.metric("F1 Score", f"{f1*100:.2f}%")

st.divider()

# 🔥 PLACEHOLDERS
reading_placeholder = st.empty()
alert_placeholder = st.empty()
metric_placeholder = st.empty()
chart_placeholder = st.empty()

# 🔥 SESSION STATE DATA
if "data" not in st.session_state:
    st.session_state.data = []

data = st.session_state.data

# 🔁 SINGLE RUN
try:
    line = ser.readline().decode(errors='ignore').strip()

    if not line:
        reading_placeholder.warning("⚠️ Waiting for sensor data...")
    else:
        values = line.split(",")

        if len(values) == 3:
            try:
                temp = float(values[0])
                current = float(values[1])
            except:
                temp, current = 0, 0

            # 📊 STORE DATA
            data.append([temp, current])
            df = pd.DataFrame(data, columns=["temperature", "current"])

            # 🔥 MODEL PREDICTION
            scaled_input = scaler.transform([[temp, current]])
            pred = model.predict(scaled_input)
            latest_anomaly = 1 if pred[0] == -1 else 0

            # 🔥 REAL-WORLD NOISE FIX
            if current < 0.15:
                latest_anomaly = 0
            if temp < 30 and current < 1:
                latest_anomaly = 0

            # 🔥 BUZZER CONTROL
            try:
                if latest_anomaly:
                    ser.write(b'1')
                else:
                    ser.write(b'0')
            except:
                pass

            # 🎯 LIVE DISPLAY
            with reading_placeholder.container():
                st.subheader("📡 Live Sensor Readings")

                colA, colB, colC = st.columns(3)
                colA.metric("🌡️ Temperature", f"{temp:.2f} °C")
                colB.metric("⚡ Current", f"{current:.2f} A")
                colC.metric("🚨 Status", "ANOMALY" if latest_anomaly else "NORMAL")

                st.caption(f"Last Update: {time.strftime('%H:%M:%S')}")

            # 🚨 ALERT
            with alert_placeholder.container():
                if latest_anomaly:
                    st.error("🚨 Anomaly Detected! Buzzer Activated")
                else:
                    st.success("✅ System Normal")

            # 📊 ANOMALY COUNT
            anomaly_count = 0
            for row in data:
                scaled = scaler.transform([row])
                if model.predict(scaled)[0] == -1:
                    anomaly_count += 1

            metric_placeholder.metric(
                "Total Anomalies",
                f"{anomaly_count}/{len(data)}"
            )

            # 📈 GRAPH
            fig = px.scatter(
                df,
                x="temperature",
                y="current",
                title="Live Sensor Data"
            )

            chart_placeholder.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Runtime Error: {e}")

# 🔄 AUTO REFRESH
time.sleep(2)
st.rerun()