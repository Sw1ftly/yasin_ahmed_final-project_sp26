import os
import uuid
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from config import Config


def load_training_data(data_path='data/enriched_features.csv'):
    """Load enriched feature dataset. Falls back to synthetic data if not present."""
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        X = df[['age', 'gender_code', 'state_risk', 'urban_code']].values
        y = df[['diabetes', 'cardio', 'obesity', 'respiratory']].values
    else:
        print('No enriched dataset found — generating synthetic training data.')
        X, y = _generate_synthetic_data(n=2000)
    return X, y


def _generate_synthetic_data(n=2000):
    rng = np.random.RandomState(42)
    age         = rng.randint(18, 80, n)
    gender_code = rng.randint(0, 2, n)
    state_risk  = rng.randint(0, 3, n)
    urban_code  = rng.randint(0, 3, n)

    X = np.column_stack([age, gender_code, state_risk, urban_code])

    # Labels with realistic correlations
    diabetes    = ((age > 50) & (state_risk >= 1)).astype(int)
    diabetes    = np.where(rng.rand(n) < 0.15, 1 - diabetes, diabetes)
    cardio      = ((age > 45) & ((gender_code == 1) | (state_risk == 2))).astype(int)
    cardio      = np.where(rng.rand(n) < 0.12, 1 - cardio, cardio)
    obesity     = ((state_risk >= 1) & (urban_code < 2)).astype(int)
    obesity     = np.where(rng.rand(n) < 0.18, 1 - obesity, obesity)
    respiratory = ((urban_code == 0) | (age > 55)).astype(int)
    respiratory = np.where(rng.rand(n) < 0.20, 1 - respiratory, respiratory)

    y = np.column_stack([diabetes, cardio, obesity, respiratory])
    return X, y


def train_model(data_path='data/enriched_features.csv',
                model_path=None,
                auc_threshold=0.65):
    model_path = model_path or Config.MODEL_PATH
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    X, y = load_training_data(data_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf  = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    clf = MultiOutputClassifier(rf)
    clf.fit(X_train, y_train)

    # Evaluate
    aucs = []
    for i in range(y_test.shape[1]):
        proba = clf.estimators_[i].predict_proba(X_test)[:, 1]
        try:
            aucs.append(roc_auc_score(y_test[:, i], proba))
        except Exception:
            aucs.append(0.5)
    mean_auc = np.mean(aucs)

    label_names = ['diabetes', 'cardio', 'obesity', 'respiratory']
    print(f'\nModel evaluation:')
    for name, auc in zip(label_names, aucs):
        print(f'  {name}: AUC = {auc:.4f}')
    print(f'  Mean AUC: {mean_auc:.4f}')

    if mean_auc >= auc_threshold:
        joblib.dump(clf, model_path)
        new_version = 'rf_chronic_v' + str(uuid.uuid4())[:4]
        print(f'\nModel promoted and saved to {model_path}')
        print(f'New model version tag: {new_version}')
        return True, mean_auc, new_version
    else:
        print(f'\nMean AUC {mean_auc:.4f} below threshold {auc_threshold}. Model NOT promoted.')
        return False, mean_auc, None