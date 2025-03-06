from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from myapp.models.user import User
from myapp import db, login_manager, limiter
from myapp.forms.registration_form import RegistrationForm
from myapp.forms.login_form import LoginForm
from flask_limiter.util import get_remote_address

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_login_limit():
    return current_app.config['LOGIN_LIMIT']

@auth_bp.route('/login', methods=['POST'])
@limiter.limit(get_login_limit, key_func=get_remote_address)
def login():
    data = request.get_json()
    form = LoginForm(data=data)

    if not form.validate():
        return jsonify({'error': form.errors}), 400

    username = form.username.data
    password = form.password.data

    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    login_user(user)
    return jsonify({'message': 'Logged in', 'user_id': user.id}), 200


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200

def get_signup_limit():
    return current_app.config['SIGNUP_LIMIT']

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit(get_signup_limit, key_func=get_remote_address)
def signup():
    data = request.get_json()
    form = RegistrationForm(data=data)

    if not form.validate():
        return jsonify({'error': form.errors}), 400

    username = form.username.data
    password = form.password.data

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already in use'}), 400

    new_user = User(username=username)
    new_user.password = password

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500

    return jsonify({'message': 'User created', 'user_id': new_user.id}), 201


@auth_bp.route('/', methods=['GET'])
def home():
    user = current_user

    if user.is_authenticated:
        return jsonify({'message': 'Hello, {}! You are logged in.'.format(user.username)}), 200
    else:
        return jsonify({'message': 'Hello, guest!'}), 200