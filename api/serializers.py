from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError

from api.models import Teacher, Student, User, Course

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, clean_data):
        user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
        user_obj.username = clean_data['username']
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    ##
    def check_user(self, clean_data):
        user = authenticate(username=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError('user not found')
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username')


class CourseCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        existing_name = Course.objects.filter(name=value).first()

        if existing_name:
            raise ValidationError("A course with this name already exists.")

    # def create(self, validated_data):
    #     a


class CourseEnrollSerializer(serializers.Serializer):
    code = serializers.CharField()

    def check_code(self, clean_data):
        enrolled = authenticate(code=clean_data['code'])
        if not enrolled:
            raise ValidationError('code not found')
        return enrolled


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'code', 'created_by_teacher', 'created_at')
        read_only_fields = ['code', 'created_by_teacher', 'created_at']
