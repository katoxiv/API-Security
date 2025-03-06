from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
from myapp.models.user import User
from wtforms_alchemy import Unique, ModelForm
from myapp import db
import bleach


class RegistrationForm(ModelForm):
    username = StringField(
        'Username', 
        validators=[
            DataRequired(),
            Length(min=4, max=25),
            Unique(User.username, get_session=lambda: db.session),
            Regexp(r'^[a-zA-Z0-9_]+$', message='Username should contain only letters, numbers, and underscores.')
        ]
    )

    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),
            Length(min=8),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=])[^\s]{8,}$',
                message='Password should contain at least one lowercase letter, one uppercase letter, one digit, and one special character (@#$%^&+=).'
            )
        ]
    )

    confirm = PasswordField(
        'Repeat Password', 
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    def validate(self):
        if not super().validate():
            return False
        self.sanitize_input()
        return True

    def sanitize_input(self):
        self.username.data = bleach.clean(self.username.data.strip().lower())
        self.password.data = bleach.clean(self.password.data.strip())
