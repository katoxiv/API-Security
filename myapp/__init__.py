from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object('myapp.config.Config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    limiter.init_app(app)

    # Import blueprints
    from myapp.services.auth import auth_bp
    from myapp.services.calculate_service import calculate_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(calculate_bp)

    # Error handlers
    @app.errorhandler(500)
    def handle_error(e):
        return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({'error': 'Unauthorized'}), 401

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({'error': 'Bad request'}), 400

    return app

app = create_app()