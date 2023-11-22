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
    name = models.CharField

class Lesson(models.Model):
   name = models.CharField(max_length=255)
   link = models.URLField()
   topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

class Section(models.Model):
   section_no = models.IntegerField()
   no_of_questions = models.IntegerField()
   lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

class AssessmentType(models.Model):
    name = models.CharField(max_length=255)

class Assessment(models.Model):
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)


class Question(models.Model):
    question_no = models.IntegerField()
    question = models.TextField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

class Response(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField()
   