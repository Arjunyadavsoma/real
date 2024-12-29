from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize the extensions outside of the app to avoid circular imports
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Local import to avoid circular import
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  # Load config from 'config.py'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    
    # Configure the login view
    login_manager.login_view = 'main.login'  # Redirect to the login page if not authenticated
    
    # Register blueprints
    from app.routes import main_bp  # Local import to avoid circular import
    app.register_blueprint(main_bp)
    
    return app
