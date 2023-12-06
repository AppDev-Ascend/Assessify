from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from . import assessment_generator

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
    TYPE_CHOICES = [('multiple choice', 'Multiple Choice'), ('identification', 'Identification'),('true or false', 'True or False'), ('fill in the blanks', 'Fill in the Blanks'), ('essay', 'Essay')]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False)
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
        self.no_of_questions = int(data['no_of_questions'])
        self.learning_outcomes = data['learning_outcomes']
        self.user = data['user']
        self.save()

        # API CALL
        ai = assessment_generator.AssessmentGenerator()
        questions = ai.get_quiz(self.lesson, self.type, self.no_of_questions, self.learning_outcomes)

        # # SAMPLE API CALL RESULT
        # questions = {"type": "Multiple Choice",
        #              "questions":
        #                  [
        #                      {
        #                          "question": "What is the purpose of the Prototype pattern?",
        #                          "options": [
        #                              "To create new objects from scratch",
        #                              "To copy an existing object as a blueprint for creating new objects",
        #                              "To reduce the complexity of object creation",
        #                              "To maintain object relationships"
        #                          ],
        #                          "answer": 2
        #                      },
        #                      {
        #                          "question": "Which component is responsible for creating new objects using the Prototype pattern?",
        #                          "options": [
        #                              "Prototype",
        #                              "Concrete Prototype",
        #                              "Client",
        #                              "Prototype Registry"
        #                          ],
        #                          "answer": 3
        #                      },
        #                      {
        #                          "question": "When is the Prototype pattern useful?",
        #                          "options": [
        #                              "When object creation is more efficient by copying an existing object",
        #                              "When a class cannot anticipate the type of objects it must create",
        #                              "When configuring complex objects with different properties",
        #                              "All of the above"
        #                          ],
        #                          "answer": 4
        #                      },
        #                      {
        #                          "question": "What are the pros of using the Prototype pattern?",
        #                          "options": [
        #                              "Object creation efficiency and flexible object creation",
        #                              "Reduced complexity and maintains object relationships",
        #                              "Efficient cloning and reduced need for proper initialization",
        #                              "All of the above"
        #                          ],
        #                          "answer": 4
        #                      },
        #                      {
        #                          "question": "What are the cons of using the Prototype pattern?",
        #                          "options": [
        #                              "Cloning complexity and potential for inefficient cloning",
        #                              "Need for proper initialization and maintaining prototypes",
        #                              "Object creation efficiency and reduced complexity",
        #                              "All of the above"
        #                          ],
        #                          "answer": 1
        #                      }
        #                  ]
        #              }
        questions_list = {'assessment': self, 'questions': questions['questions']}
        for i, q in enumerate(questions_list['questions']):
            question = Question()
            question.add_question(no=i + 1, question=q['question'], answer=q['answer'], assessment=self)
            options_list = q['options']
            for j, o in enumerate(options_list):
                option = Option()
                option.add_option(question=question, option_no=j + 1, option=o)

        return questions_list


class Question(models.Model):
    question_no = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    def add_question(self, no, question, answer, assessment):
        self.question_no = no
        self.question = question
        self.answer = answer
        self.assessment = assessment
        self.save()
        return self


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=False)
    option_no = models.IntegerField(null=False)
    option = models.TextField(null=False)

    def add_option(self, question, option_no, option):
        self.question = question
        self.option_no = option_no
        self.option = option
        self.save()
        return self
