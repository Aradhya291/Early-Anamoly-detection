import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# 📂 Load dataset (UPDATED PATH)
df = pd.read_csv("well_separated_dataset.csv")

# ✅ Features
X = df[['temperature', 'current']]

# ✅ Ground truth
y = df['status'].apply(lambda x: 0 if x == "NORMAL" else 1)

# 🔥 Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 🔥 Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 🔥 MODEL (FINAL TUNED)
model = IsolationForest(
    contamination=0.25,   # balanced
    n_estimators=300,
    random_state=42
)

# Train model
model.fit(X_train_scaled)

# Predict
preds = model.predict(X_test_scaled)

# Convert output
y_pred = [0 if p == 1 else 1 for p in preds]

# 📊 METRICS
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n📊 FINAL MODEL PERFORMANCE")
print("Accuracy :", round(accuracy * 100, 2), "%")
print("Precision:", round(precision * 100, 2), "%")
print("Recall   :", round(recall * 100, 2), "%")
print("F1 Score :", round(f1 * 100, 2), "%")

# 📊 CONFUSION MATRIX
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:\n", cm)

# 📊 CLASSIFICATION REPORT
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# 💾 SAVE MODEL + SCALER
joblib.dump(model, "isolation_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\n✅ Model & scaler saved!")

# 📈 VISUALIZATION
plt.figure(figsize=(6,5))
plt.scatter(X_test['temperature'], X_test['current'], c=y_pred)
plt.xlabel("Temperature")
plt.ylabel("Current")
plt.title("Anomaly Detection (Test Data)")
plt.show()

# 🔥 THRESHOLD COMPARISON (EXTRA)
threshold_pred = [
    1 if (t > 35 or c > 2) else 0
    for t, c in zip(X_test['temperature'], X_test['current'])
]

threshold_accuracy = accuracy_score(y_test, threshold_pred)

print("\n🔍 Threshold vs ML Comparison")
print("Threshold Accuracy:", round(threshold_accuracy * 100, 2), "%")
print("ML Accuracy       :", round(accuracy * 100, 2), "%")