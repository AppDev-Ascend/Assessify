from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate, login
from django.core.exceptions import ValidationError

from api.models import Assessment, User
from api.validations import login_validation, register_validation, validate_assessment

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'username', 'password']

    def create(self, data):
        try:
            register_validation(data)
            email = data['email']
            username = data['username']
            password = data['password']
            user = UserModel.objects.create_user(email, username, password)
            return user
        except ValidationError as e:
            raise ValidationError(e.message)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, data):
        try:
            user = login_validation(data)
            return user
        except ValidationError as e:
            raise ValidationError(e.message)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['user_id', 'email', 'username']


class AssessmentsSerializer(serializers.Serializer):

    def get_assessments(self, user_id):
        assessments = Assessment.objects.filter(user_id=user_id).values()
        return assessments


class AssessmentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            'name',
            'type',
            'description',
            'lesson',
            'no_of_questions',
            'learning_outcomes',
            'user'
        ]

    def create(self, data):
        try:
            validated_data = validate_assessment(data)
            assessment = Assessment(**validated_data)
            assessment.add_assessment(validated_data)
            return assessment
        except ValidationError as e:
            raise ValidationError(e.message)
