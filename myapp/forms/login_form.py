# /forms/login_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import bleach

class LoginForm(FlaskForm):
    class Meta:
        csrf = False
        
    username = StringField(
        'Username', 
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password', 
        validators=[DataRequired()]
    )

    def validate(self):
        if not super().validate():
            return False
        self.sanitize_input()
        return True

    def sanitize_input(self):
        self.username.data = bleach.clean(self.username.data.strip().lower())
        self.password.data = bleach.clean(self.password.data.strip())
