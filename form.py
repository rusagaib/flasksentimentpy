from flask_wtf import FlaskForm
# from flask_wtf.file import FileField
# from wtforms import SubmitField
# from werkzeug.utils import secure_filename

# from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
# from werkzeug.utils import secure_filename

# from pwd_hash import cry_pwd
import re

class DocumentUploadForm(FlaskForm):
    # file = FileField('File')
    document = FileField('Document', validators=[FileRequired(), FileAllowed(['xlsx'], 'Excel Document only!')])
    submit = SubmitField(label=('submit'))
    # submit = SubmitField('Submit')

class LoginUserForm(FlaskForm):
    username = StringField(label=('username'),
        validators=[DataRequired()])
    password = PasswordField(label=('password'),
        validators=[DataRequired()])
    submit = SubmitField(label=('submit'))

    def clean_username(self, username):
        filter = re.sub(r'[^\w]', ' ', self.username.data)
        pattern = re.compile(r'\s+')
        str = re.sub(pattern, '', filter)
        return str

    # def hash_password(self, password):
    #     password = gen_pwd(self.password.data)
    #     return password

    # def validate_username(self, username):
    #     excluded_chars = " *?!'^+%&/()=}][{$#"
    #     for char in self.username.data:
    #         if char in excluded_chars:
    #             return ValidationError(f"Character {char} is not allowed in username.")
    #         else:
    #             return "valid"
