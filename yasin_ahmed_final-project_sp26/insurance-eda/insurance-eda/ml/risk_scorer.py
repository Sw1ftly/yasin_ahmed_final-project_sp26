import uuid
import joblib
import numpy as np
from datetime import date
from config import Config
from app.models import HealthRiskScore


def _build_feature_vector(customer):
    """Build the feature vector for the ML model from customer demographics."""
    age = customer.age or 40
    gender_code = 1 if customer.Gender == 'Male' else 0

    # State risk index based on CDC regional data approximation
    high_risk_states = {'MS', 'AL', 'WV', 'LA', 'AR', 'OK', 'TN', 'KY', 'SC', 'GA'}
    med_risk_states  = {'TX', 'MO', 'IN', 'OH', 'MI', 'NC', 'PA', 'FL', 'AZ', 'NM'}
    state = customer.StateCode or 'NY'
    if state in high_risk_states:
        state_risk = 2
    elif state in med_risk_states:
        state_risk = 1
    else:
        state_risk = 0

    # ZIP-based urban code approximation
    zipcode = customer.ZipCode or '10001'
    try:
        first_digit = int(zipcode[0])
        urban_code = 2 if first_digit in [0, 1, 9] else (1 if first_digit in [2, 3, 6, 7] else 0)
    except Exception:
        urban_code = 1

    return np.array([[age, gender_code, state_risk, urban_code]])


def _score_local(customer):
    """Score using local sklearn model."""
    try:
        model = joblib.load(Config.MODEL_PATH)
    except FileNotFoundError:
        # Model not trained yet — return neutral scores
        return 0.30, 0.25, 0.28, 0.20

    features = _build_feature_vector(customer)
    probs = model.predict_proba(features)
    # probs is a list of arrays, one per output
    d = float(probs[0][0][1]) if len(probs[0][0]) > 1 else 0.30
    c = float(probs[1][0][1]) if len(probs[1][0]) > 1 else 0.25
    o = float(probs[2][0][1]) if len(probs[2][0]) > 1 else 0.28
    r = float(probs[3][0][1]) if len(probs[3][0]) > 1 else 0.20
    return d, c, o, r


def _score_azure(customer):
    """Score using Azure ML real-time endpoint."""
    import requests, json
    features = _build_feature_vector(customer).tolist()
    payload  = json.dumps({'data': features})
    headers  = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {Config.AZURE_ML_KEY}'
    }
    resp = requests.post(Config.AZURE_ML_ENDPOINT, data=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    return (result['diabetes'], result['cardio'],
            result['obesity'], result['respiratory'])


def get_or_refresh_score(customer, db_session):
    """Return the latest risk score, creating a new one if stale or missing."""
    latest = customer.latest_risk_score
    if latest and not latest.is_stale:
        return latest

    if Config.USE_LOCAL_ML:
        d, c, o, r = _score_local(customer)
    else:
        d, c, o, r = _score_azure(customer)

    score = HealthRiskScore(
        RiskScoreID     = 'RSK-' + str(uuid.uuid4())[:8].upper(),
        CustomerID      = customer.CustomerID,
        ScoreDate       = date.today(),
        DiabetesRisk    = round(d, 4),
        CardioRisk      = round(c, 4),
        ObesityRisk     = round(o, 4),
        RespiratoryRisk = round(r, 4),
        ScoringModel    = Config.ACTIVE_MODEL_VERSION,
    )
    db_session.add(score)
    db_session.flush()
    customer.health_risk_scores.insert(0, score)
    return score