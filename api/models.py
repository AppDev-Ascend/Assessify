from django.db import models
from django.contrib.auth.models import AbstractUser

# User
class User(AbstractUser):
    display_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_id = models.IntegerField()


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacher_id = models.IntegerField()

# Educational System
class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField
