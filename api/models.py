from django.db import models
from django.contrib.auth.models import AbstractUser

# User
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.crypto import get_random_string


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return self.username


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    # def __str__(self):
    #     user = self.user
    #     if user:
    #         name = f"{user.lastname}, {user.firstname}"
    #         return f"{self.student_id} - {name}"
    #     return f"{self.student_id} - No User"


class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)

    # def __str__(self):
    #     user = self.user
    #     if user:
    #         name = f"{user.lastname}, {user.firstname}"
    #         return f"{self.teacher_id} - {name}"
    #     return f"{self.teacher_id} - No User"


# Educational System
class Course(models.Model):
    name = models.CharField
    code = models.CharField(max_length=10, unique=True, default=get_random_string(10))
    created_by_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    enrollment = models.ManyToManyField(Student, related_name="enrollment")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Course, on_delete=models.CASCADE)


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
