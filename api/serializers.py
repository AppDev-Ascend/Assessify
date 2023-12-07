from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate, login
from django.core.exceptions import ValidationError

from .models import Assessment, User, Question, Option

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        return UserModel.objects.create_user(email=validated_data['email'], 
                                             username=validated_data['username'], 
                                             password=validated_data['password'])


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username')

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = (
            'name',
            'type',
            'description',
            'lesson',
            'no_of_questions',
            'learning_outcomes',
        )

class AssessmentsSerializer(serializers.Serializer):

    def get_assessments(self, user_id):
        assessments = Assessment.objects.filter(user_id=user_id).values()
        return assessments


class AssessmentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = (
            'name',
            'type',
            'description',
            'lesson',
            'no_of_questions',
            'learning_outcomes',
            'user'
        )

    def create(self, validated_data):
        u = User.objects.get(user_id=validated_data['user'])
        assessment = Assessment.objects.create(
            name=validated_data['name'],
            type=validated_data['type'],
            description=validated_data['description'],
            lesson=validated_data['lesson'],
            no_of_questions=validated_data['no_of_questions'],
            learning_outcomes=validated_data['learning_outcomes'],
            user=u
        )
        assessment.create_questions()
        return assessment


class AssessmentQuestionSerializer(serializers.Serializer):
    question_no = serializers.IntegerField()
    question = serializers.CharField()
    answer = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField())

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        for option_text in options_data:
            Option.objects.create(question=question, option=option_text)
        return question
    
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'question_no',
            'question',
            'answer'      
        )
        
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = (
            'option_no',
            'option'
        )