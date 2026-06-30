import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb


def train_models(dataset_path="dataset.csv"):
    df = pd.read_csv(dataset_path)

    if "bug" not in df.columns:
        raise ValueError("Dataset must contain 'bug' column (0 or 1).")

    X = df.drop("bug", axis=1)
    y = df["bug"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)

    rf_f1 = f1_score(y_test, rf_pred)
    rf_acc = accuracy_score(y_test, rf_pred)

    xgb_model = xgb.XGBClassifier(
        n_estimators=300,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
    )

    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)

    xgb_f1 = f1_score(y_test, xgb_pred)
    xgb_acc = accuracy_score(y_test, xgb_pred)

    print("\nRandomForest Metrics:")
    print("Accuracy:", rf_acc)
    print("F1 Score:", rf_f1)
    print(classification_report(y_test, rf_pred))

    print("\nXGBoost Metrics:")
    print("Accuracy:", xgb_acc)
    print("F1 Score:", xgb_f1)
    print(classification_report(y_test, xgb_pred))

    joblib.dump(rf_model, "astra_rf_model.pkl")
    joblib.dump(xgb_model, "astra_xgb_model.pkl")

    print("\nModels saved:")
    print("astra_rf_model.pkl")
    print("astra_xgb_model.pkl")

    return {
        "random_forest": {"accuracy": rf_acc, "f1_score": rf_f1},
        "xgboost": {"accuracy": xgb_acc, "f1_score": xgb_f1},
    }
