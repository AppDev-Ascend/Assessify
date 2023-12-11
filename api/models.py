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
    TYPE_CHOICES = [('quiz', 'Quiz'), ('exam', 'Exam')]
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=128, null=False, unique=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False)
    description = models.TextField()
    lesson = models.TextField()
    no_of_questions = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def create_quiz(self, q_type, l_outcomes):
        # API CALL
        # ai = assessment_generator.AI()
        # questions = ai.get_quiz(self.lesson, type, self.no_of_questions, self.learning_outcomes)

        # SAMPLE API CALL RESULT
        quiz = {"type": "Multiple Choice",
                     "questions":
                         [
                             {
                                 "question": "What is the purpose of the Prototype pattern?",
                                 "options": [
                                     "To create new objects from scratch",
                                     "To copy an existing object as a blueprint for creating new objects",
                                     "To reduce the complexity of object creation",
                                     "To maintain object relationships"
                                 ],
                                 "answer": 2
                             },
                             {
                                 "question": "Which component is responsible for creating new objects using the Prototype pattern?",
                                 "options": [
                                     "Prototype",
                                     "Concrete Prototype",
                                     "Client",
                                     "Prototype Registry"
                                 ],
                                 "answer": 3
                             },
                             {
                                 "question": "When is the Prototype pattern useful?",
                                 "options": [
                                     "When object creation is more efficient by copying an existing object",
                                     "When a class cannot anticipate the type of objects it must create",
                                     "When configuring complex objects with different properties",
                                     "All of the above"
                                 ],
                                 "answer": 4
                             },
                             {
                                 "question": "What are the pros of using the Prototype pattern?",
                                 "options": [
                                     "Object creation efficiency and flexible object creation",
                                     "Reduced complexity and maintains object relationships",
                                     "Efficient cloning and reduced need for proper initialization",
                                     "All of the above"
                                 ],
                                 "answer": 4
                             },
                             {
                                 "question": "What are the cons of using the Prototype pattern?",
                                 "options": [
                                     "Cloning complexity and potential for inefficient cloning",
                                     "Need for proper initialization and maintaining prototypes",
                                     "Object creation efficiency and reduced complexity",
                                     "All of the above"
                                 ],
                                 "answer": 1
                             }
                         ]
                     }
        
        qt = Question_Type.objects.get(name=q_type)
        questions_list = {'questions': quiz['questions']}
        s = Section.objects.create(
            section_no=1, 
            type=q_type[0], 
            assessment=self
        )
        for l in l_outcomes:
            Learning_Outcomes.objects.create(
                learning_outcome=l, 
                section=s
            )
        for i, q in enumerate(questions_list['questions']):
            question = Question.objects.create(
                question_no=i + 1,
                question=q['question'],
                answer=q['answer'],
                section=s
            )
            if qt.name == 'multiple choice' or qt.name == 'true or false':
                options_list = q['options']
                for j, o in enumerate(options_list):
                    option = Option.objects.create(
                        option_no=j + 1,
                        option=o,
                        question=question
                )

        return self
    
    def create_exam(self, q_type, l_outcomes):
        # API CALL
        # ai = assessment_generator.AI()
        # questions = ai.get_exam(self.lesson, type, self.no_of_questions, self.learning_outcomes)
        
        # SAMPLE API CALL RESULT
        exam = {
            "type": "Exam",
            "sections": [
                {
                    "section_name": "Test 1",
                    "section_type": "Multiple Choice",
                    "questions": [
                        {
                            "question": "What is the purpose of the Prototype Design Pattern?",
                            "options": [
                                "To create new game characters in game development",
                                "To save time and resources in creating similar GUI components",
                                "To clone database records in working with databases",
                                "To evaluate the architectural context of an application"
                            ],
                            "answer": 2
                        },
                        {
                            "question": "What is a benefit of using the Prototype Design Pattern?",
                            "options": [
                                "It allows for the creation of new game characters",
                                "It saves time and resources in generating similar UI elements",
                                "It provides a clear and complete documentation of prototype objects",
                                "It ensures consistent behavior and initial states of cloned objects"
                            ],
                            "answer": 3
                        }
                    ]
                },
                {
                    "section_name": "Test 2",
                    "section_type": "True or False",
                    "questions": [
                        {
                            "question": "The Prototype Design Pattern is used in software development to create new objects by copying existing objects.",
                            "answer": "True"
                        },
                        {
                            "question": "The Prototype Design Pattern is used in game development to create new game characters with different attributes.",
                            "answer": "True"
                        }
                    ]
                },
                {
                    "section_name": "Test 2",
                    "section_type": "Essay",
                    "questions": [
                        {
                            "question": "1. Explain the concept of the Prototype Design Pattern and how it is used in software development. What are the key characteristics of this pattern?"
                        },
                        {
                            "question": "2. Discuss the benefits of using the Prototype Design Pattern in game development. How does it help in creating new game characters with different attributes?"
                        },
                        {
                            "question": "3. Describe a real-world example where the Prototype Design Pattern can be applied in graphical user interfaces. How does it save time and resources when generating similar UI elements?"
                        },
                        {
                            "question": "4. Discuss the drawbacks or limitations of using the Prototype Design Pattern in database operations. When might it not be suitable for cloning database records?"
                        },
                        {
                            "question": "5. Explain the importance of maintaining consistency when using the Prototype Design Pattern. How can it ensure that all cloned objects derived from the same prototype exhibit consistent behavior and initial states?"
                        }
                    ]
                }
            ]
        }
        
        qt = Question_Type.objects.get(name=q_type)
        section_list = {'sections': exam['sections']}
        
        for l in l_outcomes:
            Learning_Outcomes.objects.create(
                learning_outcome=l, 
                section=s
            )
            
        for i, s in enumerate(section_list['sections'], start=1):
            s = Section.objects.create(
                section_no=i, 
                name=s['section_name'],
                type=s['section_type'], 
                assessment=self
            )
            for j, q in enumerate(s ['questions'], start=1):
                question = Question.objects.create(
                    question_no=j,
                    question=q['question'],
                    answer=q['answer'],
                    section=s
                )
                if qt.name == 'multiple choice' or qt.name == 'true or false':
                    options_list = q['options']
                    for k, o in enumerate(options_list, start=1):
                        option = Option.objects.create(
                            option_no=k,
                            option=o,
                            question=question
                    )
        
class Question_Type(models.Model):
    name = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class Section(models.Model):
    section_no = models.IntegerField(null=False)
    name = models.CharField(max_length= 64)
    type = models.ForeignKey(Question_Type, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return f'Section {self.section_no} of assessment-{self.assessment.pk}'

class Learning_Outcomes(models.Model):
    learning_outcome = models.CharField(max_length=256, null=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f'{self.learning_outcome} for section {self.section.pk}'

class Question(models.Model):
    question_no = models.IntegerField(null=False)
    question = models.TextField(null=False)
    answer = models.TextField(null=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.question


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=False)
    option_no = models.IntegerField(null=False)
    option = models.TextField(null=False)
    
    def __str__(self):
        return self.option
