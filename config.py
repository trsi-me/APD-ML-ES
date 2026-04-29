import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'apd-ml-es-dev-key-change-in-production')
    ADMIN_PATH = os.environ.get('ADMIN_PATH', 'c9a4m7-p2k8-qv1r')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Adm!APD2026#Local')
