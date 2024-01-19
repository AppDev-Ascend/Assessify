from django.db import models, transaction
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
    TYPE_CHOICES = [('quiz', 'Quiz'), ('exam', 'Exam')]
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, null=False)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False)
    description = models.TextField()
    lesson_path = models.TextField()
    no_of_questions = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    @transaction.atomic
    def create_quiz(self, section):
        # section consists of:
        # ['section_types'] = list i.e. ['multiple choice']
        # ['section_lengths'] = list i.e. [5]
        # ['learning_outcomes'] = list i.e. ['l_outcome 1.1', 'l_outcome 1.2', 'l_outcome 1.3']
        
        s_type = section['section_types'][0]
        s_length = section['section_lengths'][0]
        l_outcomes = section['learning_outcomes']
        
        # API CALL
        ai = assessment_generator.AssessmentGenerator()
        quiz = ai.get_quiz(self.user.username, s_type, s_length, l_outcomes, self.lesson_path)
        
        qt = Question_Type.objects.get(type=s_type)
        questions_list = {'questions': quiz['questions']}
        
        s = Section.objects.create(
            section_no=1, 
            length=s_length,
            type=qt, 
            assessment=self
        )
        for l in l_outcomes:
            Learning_Outcomes.objects.create(
                learning_outcome=l, 
                section=s
            )
        for i, q in enumerate(questions_list['questions'], start=1):
            
            if qt.type == 'essay' or qt.type == 'Essay':
                question = Question.objects.create(
                question_no=i,
                question=q['question'],
                answer=[],
                section=s
                )
            else:
                print(q)
                question = Question.objects.create(
                    question_no=i,
                    question=q['question'],
                    answer=q['answer'],
                    section=s
                )
                
            if qt.type.lower() in ['multiple choice']:
                options_list = q['options']
                for j, o in enumerate(options_list, start=0):
                    option = Option.objects.create(
                        option_no=j,
                        option=o,
                        question=question
                    )

        return self
    
    @transaction.atomic
    def create_exam(self, section):
        # section consists of:
        # ['section_types'] = list i.e. ['multiple choice', 'true or false', 'essay']
        # ['section_lengths'] = list i.e. [5, 10, 15,]
        # ['learning_outcomes'] = list i.e. [['l_outcome 1.1', 'l_outcome 1.2',], ['l_outcome 2.1', 'l_outcome 2.2']]
        
        exam_format = []

        for i in range(len(section['section_types'])):
            
            s_type = section['section_types'][i]
            s_length = section['section_lengths'][i]
            l_outcome = section['learning_outcomes'][i] if i < len(section['learning_outcomes']) else []

            exam_format.append((s_type, s_length, l_outcome))

        # API CALL
        ai = assessment_generator.AssessmentGenerator()
        exam = ai.get_exam(self.user.username, exam_format, self.lesson_path)
        
        section_list = {'sections': exam['sections']}
        
        s_types = section['section_types']
        s_lengths = section['section_lengths']
        l_outcomes = section['learning_outcomes']

        if l_outcomes == []:
            l_outcomes = [[] for i in range(len(s_types))]

        for i, (s, s_l, l) in enumerate(zip(section_list['sections'], s_lengths, l_outcomes), start=1):

            s_type = s['type'].lower()
            print(f's_type: {s_type}')
            s_t = Question_Type.objects.get(type=s_type)
            sec = Section.objects.create(
                section_no=i, 
                name=s['name'],
                length=s_l,
                type=s_t, 
                assessment=self
            )
            for lo in l:
                Learning_Outcomes.objects.create(
                    learning_outcome=lo, 
                    section=sec
                )
            for j, q in enumerate(s['questions'], start=1):
                
                if s_type == 'essay':
                    answer = ''
                else:
                    answer = q['answer']
                    print(answer)
                    
                question = Question.objects.create(
                    question_no=j,
                    question=q['question'],
                    answer=answer,
                    section=sec
                )
                
                if s_type == 'multiple choice':
                    options_list = q['options']
                    for k, o in enumerate(options_list, start=0):
                        option = Option.objects.create(
                            option_no=k,
                            option=o,
                            question=question
                    )
        
class Question_Type(models.Model):
    type = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.type

class Section(models.Model):
    section_no = models.IntegerField(null=False)
    name = models.CharField(max_length= 64)
    description = models.CharField(max_length= 64)
    length = models.IntegerField(null=False)
    type = models.ForeignKey(Question_Type, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return f'{self.pk}-{self.name}'

class Learning_Outcomes(models.Model):
    learning_outcome = models.CharField(max_length=256, null=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.learning_outcome

class Question(models.Model):
    question_no = models.IntegerField(null=False)
    question = models.TextField(null=False)
    answer = models.TextField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.question

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=False)
    option_no = models.IntegerField(null=False)
    option = models.TextField(null=False)
    
    def __str__(self):
        return self.option
