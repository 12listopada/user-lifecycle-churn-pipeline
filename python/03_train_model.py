"""
03_train_model.py
Trains a churn classification model on the features built in step 02,
evaluates it, and exports a churn score for every user.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, classification_report

feat = pd.read_csv("data/processed_features.csv")

feature_cols = ["tenure_days", "recency_days", "frequency", "monetary_total", "monetary_avg",
                 "avg_days_between_orders", "max_days_between_orders"]
X = feat[feature_cols].fillna(0)
y = feat["churned"]

# Split: 75% to train the model, 25% held back to test it honestly
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300, max_depth=6, min_samples_leaf=20,
    class_weight="balanced", random_state=42
)
model.fit(X_train, y_train)

y_proba = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_proba)
print(f"ROC-AUC: {auc:.3f}")
print(classification_report(y_test, model.predict(X_test)))

importance = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nFeature importance:")
print(importance)

# Score ALL users (not just the test set) for the final output
feat["churn_score"] = model.predict_proba(X)[:, 1].round(4)
feat["risk_band"] = pd.cut(
    feat["churn_score"], bins=[0, 0.4, 0.7, 1.0],
    labels=["Low Risk", "Medium Risk", "High Risk"]
)

feat.to_csv("data/churn_scores.csv", index=False)
print(f"\nSaved: data/churn_scores.csv")
print(feat["risk_band"].value_counts())