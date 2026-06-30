import joblib
from astra_core.ml.feature_extractor import extract_features


def predict_risk(code: str, model_path="astra_xgb_model.pkl"):
    model = joblib.load(model_path)

    features = extract_features(code)

    X = [[
        features["loc"],
        features["complexity"],
        features["num_functions"],
        features["num_imports"],
        features["num_loops"],
        features["num_conditions"],
        features["num_try"],
        features["num_classes"],
    ]]

    probability = model.predict_proba(X)[0][1]

    risk_level = "HIGH" if probability >= 0.7 else "MEDIUM" if probability >= 0.4 else "LOW"

    return {
        "probability": float(probability),
        "risk_level": risk_level,
        "features": features,
    }
