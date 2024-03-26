from flask_wtf import FlaskForm
from wtforms import StringField, DateField, EmailField, TelField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired


class ModalForm(FlaskForm):
    name = StringField("Full name: ", validators=[DataRequired()])
    dob = DateField("Date of birth: ", validators=[DataRequired()])
    email = EmailField("Email: ", validators=[DataRequired()])
    phone_number = TelField("Phone number: ", validators=[DataRequired()])
    department = StringField("Department: ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired()], )
    password =  PasswordField("Password: ", validators=[DataRequired()])
    login = SubmitField("Login")
    
class RegisterForm(FlaskForm): 
    username = StringField("Username: ", [validators.length(min=4, max=25)])
    email = EmailField("Email: ", [validators.length(min=6, max=35)]) 
    password = PasswordField("Password: ", [validators.DataRequired()])
    submit = SubmitField("Register")
    # password = PasswordField("Password: ", [validators.DataRequired(), validators.EqualTo('confirm', message="Passwords must match")])
    # confirm = PasswordField('Repeat password')
    
    
class TestForm(FlaskForm):
    name = StringField("Full name: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
