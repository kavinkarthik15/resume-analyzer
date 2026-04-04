import joblib
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_DIR = SCRIPT_DIR.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
DATASET_PATH = SCRIPT_DIR / "dataset.csv"
MODEL_PATH = MODEL_DIR / "random_forest_model.pkl"

print(f"Loading dataset from {DATASET_PATH}")
data = pd.read_csv(DATASET_PATH)
feature_columns = [col for col in data.columns if col != "shortlisted"]
X = data[feature_columns]
y = data["shortlisted"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=250,
    max_depth=12,
    min_samples_split=6,
    random_state=42,
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
probs = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
roc_auc = roc_auc_score(y_test, probs)

print(f"Model Accuracy: {accuracy * 100:.2f}%")
print(f"ROC AUC: {roc_auc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, predictions, digits=3))

joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")
print(f"Feature columns: {feature_columns}")
