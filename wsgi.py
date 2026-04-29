from app import app, initialize_app

with app.app_context():
    initialize_app()
