import os
from flask import Flask
from config import Config
from routes.main import main_bp
from routes.api import api_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from database.db import init_db
from database.seed import seed_data
from ml.trainer import train_model
from ml.predictor import load_model

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates',
    static_url_path='/static',
)

app.config.from_object('config.Config')

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/' + Config.ADMIN_PATH.strip('/'))

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PKL = os.path.join(ROOT, 'ml', 'model.pkl')


def initialize_app():
    init_db()
    seed_data()
    if not os.path.exists(MODEL_PKL):
        print('جارٍ تدريب النموذج...')
        train_model()
    load_model()
    print('تم تهيئة التطبيق بنجاح')


if __name__ == '__main__':
    with app.app_context():
        initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
