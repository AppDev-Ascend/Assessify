from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
import re

from api.models import Assessment

UserModel = get_user_model()


def register_validation(data):
    email = data['email'].strip()
    username = data['username'].strip()
    password = data['password'].strip()

    validate_email(email, "register")
    validate_username(username)
    validate_password(password)
    
    return {
        'email': email,
        'username': username,
        'password': password,
    }


def login_validation(data):
    email = data['email'].strip()
    password = data['password'].strip()

    validate_email(email, "login")
    validate_password(password)
    
    return {
        'email': email,
        'password': password
    }


def validate_email(email, type):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not email:
        raise ValidationError('an email is needed')

    if re.match(email_regex, email) is None:
        raise ValidationError('invalid email address')

    if type == "login":
        if UserModel.objects.filter(email=email).exists() is False:
            raise ValidationError('email does not exist')
    else:
        if UserModel.objects.filter(email=email).exists() is True:
            raise ValidationError('email already exists')


def validate_password(password):
    if not password:
        raise ValidationError('a password is needed')
    if len(password) < 8:
        raise ValidationError('choose another password, min 8 characters')


def validate_username(username):
    if not username:
        raise ValidationError('a username is needed')


def validate_assessment(data):
    name = data['name'].strip()
    # type = data['type'].strip()
    # description = data['description'].strip()
    # lesson = data['lesson'].strip()
    # no_of_questions = data['no_of_questions']
    # learning_outcomes = data['learning_outcomes'].strip()

    try:
        if Assessment.objects.filter(name=name).exists():
            raise ValidationError('Name already taken')
        return data
    except ValidationError as e:
        raise ValidationError(e.message)
