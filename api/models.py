from django.db import models
from django.contrib.auth.models import AbstractUser

# User
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, username, password):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']
    objects = UserManager()

    def __str__(self):
        return f"{self.user_id} - {self.username}"


class Assessment(models.Model):
    TYPE_CHOICES = [('quiz', 'Quiz'), ('exam', 'Exam')]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, null=False)
    description = models.TextField()
    lesson = models.TextField()
    no_of_questions = models.IntegerField(null=False)
    learning_outcomes = models.TextField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def add_assessment(self, data):
        self.name = data['name']
        self.type = data['type']
        self.description = data['description']
        self.lesson = data['lesson']
        self.no_of_questions = data['no_of_questions']
        self.learning_outcomes = data['learning_outcomes']
        self.user = data['user']
        self.save()

        # Dictionary containing assessment attributes
        assessment = {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'lesson': self.lesson,
            'no_of_questions': self.no_of_questions,
            'learning_outcomes': self.learning_outcomes,
            'date_created': self.date_created,
        }
        return assessment


class Question(models.Model):
    question_no = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    choices = models.TextField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
