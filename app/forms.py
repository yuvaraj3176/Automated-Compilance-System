from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RuleForm(FlaskForm):
    name = StringField('Rule Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    rule_type = SelectField('Rule Type', choices=[
        ('data_quality', 'Data Quality'),
        ('security', 'Security'),
        ('access', 'Access Control'),
        ('privacy', 'Privacy'),
        ('custom', 'Custom')
    ])
    condition = TextAreaField('Rule Condition (JSON format)', validators=[DataRequired()])
    severity = SelectField('Severity', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    submit = SubmitField('Create Rule')

class ComplianceCheckForm(FlaskForm):
    name = StringField('Check Name', validators=[DataRequired(), Length(max=100)])
    rule_id = SelectField('Select Rule', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Run Compliance Check')