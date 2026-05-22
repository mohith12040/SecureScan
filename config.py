import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cyber-security-secure-scan-secret-key-1337!')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "securescan.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Reports configuration
    REPORTS_DIR = os.path.join(BASE_DIR, 'app', 'static', 'reports')
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # ML model configuration
    TRAINED_MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')
    os.makedirs(TRAINED_MODELS_DIR, exist_ok=True)
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    os.makedirs(DATASET_DIR, exist_ok=True)
