# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = 'Everest-sprite-drink-yo'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CALCULATE_LIMIT = '50/hour'
    SIGNUP_LIMIT = '15/day'
    LOGIN_LIMIT = '6/day'
