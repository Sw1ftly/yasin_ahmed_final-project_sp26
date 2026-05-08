import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DATABASE_URL         = os.getenv("DATABASE_URL", "sqlite:///insurance_eda.db")
    SECRET_KEY           = os.getenv("SECRET_KEY", "dev-secret-key")
    USE_LOCAL_ML         = os.getenv("USE_LOCAL_ML", "true").lower() == "true"
    AZURE_ML_ENDPOINT    = os.getenv("AZURE_ML_ENDPOINT", "")
    AZURE_ML_KEY         = os.getenv("AZURE_ML_KEY", "")
    MODEL_PATH           = os.getenv("MODEL_PATH", "ml/model/rf_chronic.pkl")
    ACTIVE_MODEL_VERSION = os.getenv("ACTIVE_MODEL_VERSION", "rf_chronic_v1")
    SCORE_STALE_DAYS     = 365
    BASE_PREMIUM         = 450.00
    # Risk thresholds
    DIABETES_THRESHOLD   = 0.70
    CARDIO_THRESHOLD     = 0.70
    OBESITY_THRESHOLD    = 0.70
    RESP_THRESHOLD       = 0.70
    # Surcharge rates
    DIABETES_SURCHARGE   = 0.15
    CARDIO_SURCHARGE     = 0.10
    OBESITY_SURCHARGE    = 0.10
    RESP_SURCHARGE       = 0.05
    MAX_SURCHARGE        = 0.40