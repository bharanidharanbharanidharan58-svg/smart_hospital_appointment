import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aura_health_enterprise_secret_key_2026_x89f'
    DATABASE = os.path.join(BASE_DIR, 'aura_health.db')
    DEBUG = True
    APP_NAME = "Aura Health"
    COMPANY = "Aura Health Networks"
    VERSION = "2.5.0"
