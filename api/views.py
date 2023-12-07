import json
import os
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from .validations import login_validation, register_validation, validate_assessment
from .forms import RegisterForm, LoginForm, AssessmentAddForm, AssessmentQuestionForm, AssessmentOptionForm
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, AssessmentsSerializer, AssessmentSerializer, AssessmentAddSerializer, AssessmentQuestionSerializer
from rest_framework import permissions, status
from .converter import Converter
from .models import Assessment, User, Question, Option
from .file_handler import handle_uploaded_file, handle_non_utf8


# Notes:
# permission_classes - specifies what kind of user can enter the view
# authentication_classes - requires authentication to enter the view specifically the presence of the sessionid
# return Response() - returns a dictionary in json

class UserRegisterView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []

    # Modify for front-end here
    def get(self, request):
        # Currently for testing
        template = "api/register.html"
        form = RegisterForm()
        return render(request, template, {'form': form})

    # Returns the following JSON:
    # {"email": "user3@example.com", 
    #  "username": "user3", 
    #  "password": "pbkdf2_sha256$600000$awBXPFYxGs09qg9xAL0nTQ$uQ7+ZGbgjjlZ6FAeMFpp7AvRYEK7HwpPOuNzXjw9Ti0="}
    def post(self, request):
        try:
            data = request.data
            serializer = UserRegisterSerializer(data)
            serializer.create(data)
            return Response(serializer.data, status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.message}, status.HTTP_400_BAD_REQUEST)


# Creates a sessionid when successfully logged in
class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    # Modify for front-end here
    def get(self, request):
        # Currently for testing
        template = "api/login.html"
        form = LoginForm()
        return render(request, template, {'form': form})
    
    # Returns the following JSON:
    # {"email": "user1@example.com", 
    #  "password": "pbkdf2_sha256$600000$INUwHceAVcfMaUGycqDQ9c$bEZa715FdUFxXvp+Lr+tnH0CP2AbKKlAsOFgbRXlg6c="}
    def post(self, request):
        try:
            validated_data = login_validation(request.data)
            user = authenticate(request, 
                                email=validated_data['email'],
                                password=validated_data['password'])
            if user is not None:
                serializer = UserLoginSerializer(user)
                login(request, user)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Incorrect username or password")
        except ValidationError as e:
            return JsonResponse({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)


# Needs the logout() method to terminate the sessionid
class UserLogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class HomePageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # Modify this for front-end
    # Returns the following JSON:
    # {"user_id": 1,
    #  "email": "user1@example.com",
    #  "username": "user1"}
    def get(self, request):
        user_id = request.session['_auth_user_id']
        user = User.objects.get(user_id=user_id)
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


# List of Assessments page
# Uses session['_auth_user_id'] to get user_id
class AssessmentsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # Returns a dictionary of a list of assessments
    def get(self, request):
        user_id = request.session['_auth_user_id']
        assessments = Assessment.objects.filter(user_id=user_id)
        serializer = AssessmentsSerializer(assessments, many=True)
        # data = assessments.get_assessments(user_id)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


# Adds assessments
# Uses session['_auth_user_id'] to get user_id
class AssessmentAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # Modify here for front-end
    def get(self, request):
        # Currently for testing
        template = "api/assessment_add.html"
        form = AssessmentAddForm()
        return render(request, template, {'form': form})

    # Returns the following JSON:
    # {"assessment": {
    #     "name": "asdfas", "type": "multiple choice", "description": "asdfasdf", "lesson": "Page 1:\n\nPrototype Pattern Summary\n\nHistory\n\nThe first example of the Prototype pattern was in Ivan Sutherland's Sketchpad System in\n1964. In 1994, The Gang of Four popularized and codified the Prototype Pattern in their\nbook \"Design Patterns: Elements of Reusable Object-Oriented Software.\"\n\nDefinition\n\nA prototype pattern is a creational design pattern that focuses on creating objects by\ncopying an existing object, known as the \"prototype,\" rather than creating new instances\nfrom scratch. In this pattern, a prototype object serves as a blueprint, and new objects are\ncreated by duplicating this prototype.\n\nKey Components\n\nPrototype: The interface or abstract class that declares the methods for cloning itself.\nConcrete Prototype: The concrete classes that implement the Prototype interface or\nextend the Prototype abstract class.\n\nClient: Responsible for creating new objects by requesting the prototype to clone itself.\n\nUsages\n\nEfficient Object Creation: When object creation is more efficient by copying an existing\nobject rather than initializing a new one from scratch.\n\nReducing Subclassing: When a class cannot anticipate the type of objects it must create,\nthe Prototype Pattern allows for new object creation without relying on subclasses.\nConfiguring Objects: Allows for configuring complex objects with different properties.\n\nPros Cons\n\nObject Creation Efficiency Cloning Complexity\n\nFlexible Object Creation Need for Proper Initialization\nReduced Complexity Maintaining Prototypes\nMaintains Object Relationships Potential for Inefficient Cloning\n\nTwo ways to implement Prototype Pattern in Java\nUsing the Cloneable Interface and Creating a Custom Clone Method\n\nCloning Strategies\nShallow Copy and Deep Copy\n\nPrototype Registry: The Prototype Registry is a central repository or store that holds a\ncollection of pre-defined prototype objects.\n\nReal World Examples\n1. Creating similar video game characters with different attributes.\n2. Creating copies of GUI components (e.g., buttons, dialogs) to save time and\nresources when generating similar Ul elements.\n3. Cloning database records", "no_of_questions": 5, "learning_outcomes": "asdfasdf", "user": 1}, 
    #     "questions": [{"question": "What is the purpose of the Prototype pattern?", "answer": "2", "options": [{"option_no": 1, "option": "To create new objects from scratch"}, {"option_no": 2, "option": "To copy an existing object as a blueprint for creating new objects"}, {"option_no": 3, "option": "To reduce the complexity of object creation"}, {"option_no": 4, "option": "To maintain object relationships"}]}, 
    #                   {"question": "Which component is responsible for creating new objects using the Prototype pattern?", "answer": "3", "options": [{"option_no": 1, "option": "Prototype"}, {"option_no": 2, "option": "Concrete Prototype"}, {"option_no": 3, "option": "Client"}, {"option_no": 4, "option": "Prototype Registry"}]}, 
    #                   {"question": "When is the Prototype pattern useful?", "answer": "4", "options": [{"option_no": 1, "option": "When object creation is more efficient by copying an existing object"}, {"option_no": 2, "option": "When a class cannot anticipate the type of objects it must create"}, {"option_no": 3, "option": "When configuring complex objects with different properties"}, {"option_no": 4, "option": "All of the above"}]}, 
    #                   {"question": "What are the pros of using the Prototype pattern?", "answer": "4", "options": [{"option_no": 1, "option": "Object creation efficiency and flexible object creation"}, {"option_no": 2, "option": "Reduced complexity and maintains object relationships"}, {"option_no": 3, "option": "Efficient cloning and reduced need for proper initialization"}, {"option_no": 4, "option": "All of the above"}]}, {"question": "What are the cons of using the Prototype pattern?", "answer": "1", "options": [{"option_no": 1, "option": "Cloning complexity and potential for inefficient cloning"}, {"option_no": 2, "option": "Need for proper initialization and maintaining prototypes"}, {"option_no": 3, "option": "Object creation efficiency and reduced complexity"}, {"option_no": 4, "option": "All of the above"}]}]}
    def post(self, request):
        try:
            data_copy = request.data.copy()
            data_copy.pop('file')
            validated_data = validate_assessment(data_copy)
            user_id = request.session['_auth_user_id']
            user = User.objects.get(pk=user_id)
            validated_data['user'] = user_id
            
            if 'file' in request.FILES:
                file = request.FILES['file']
                path = os.path.join(settings.MEDIA_ROOT, 'files', file.name)
                handle_uploaded_file(file)
                file_format = file.name.split('.')[1].lower()
                lesson = ''
                
                # pdf to text convert
                if file_format == 'pdf':
                    converter = Converter()
                    lesson = converter.pdf_to_text(path)
                    
                validated_data['lesson'] = lesson
                
            else:
                print('no file')
                
            serializer = AssessmentAddSerializer(data=validated_data)
            if serializer.is_valid():
                assessment = serializer.create(validated_data)
                full_dict = {}
                full_dict['assessment'] = serializer.data
                question_list = list(Question.objects.filter(assessment=assessment))
                question_data_list = []
                
                for i, q in enumerate(question_list):
                    question_data = {
                        'question': q.question,
                        'answer': q.answer,
                        'options': list(Option.objects.filter(question=q).values('option_no', 'option'))
                    }
                    question_data_list.append(question_data)

                full_dict['questions'] = question_data_list
                request.session['assessment'] = assessment.pk
                json_data = json.dumps(full_dict)
                
                return JsonResponse(full_dict, safe=False, status=status.HTTP_200_OK)
            else:
                raise ValidationError("Invalid serializer data")
            
        except ValidationError as e:
            return JsonResponse({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        

class AssessmentQuestionsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    template_name = 'api/assessment_question.html'

    def get(self, request):
        assessment = request.session['assessment']
        questions = Question.objects.filter(assessment_id=assessment)
        q_list = list(questions)
        form_list = []

        for q in q_list:
            q_form = AssessmentQuestionForm(instance=q)
            print(q.pk)
            q_form.prefix = f'question_{q.pk}_content'  # Set a unique prefix for each question form
            form_list.append(q_form)

            options = Option.objects.filter(question_id=q.pk)
            o_list = list(options)
            for o in o_list:
                o_form = AssessmentOptionForm(instance=o)
                o_form.prefix = f'option_q-{q.pk}_o-{o.pk}_content'  # Set a unique prefix for each option form
                form_list.append(o_form)

        return render(request, template_name=self.template_name, context={'form_list': form_list})

    
    def post(self, request):
        print(request.POST.items())
        ctr = 0
        for key, value in request.POST.items():
            print(f'Key: {key}, Value: {value}')
            if key.startswith('question_'):
                string = key.split('_')
                q_id = int(string[1])
                qc = string[2].split('-')[1]
                question = Question.objects.get(id=q_id)

                if qc == "question_no":
                    # print(f'question_no: {value}')
                    question.question_no = value
                elif qc == "question":
                    # print(f'question: {value}')
                    question.question = value
                elif qc == "answer":
                    # print(f'answer: {value}')
                    question.answer = value

                question.save()

            elif key.startswith('option_'):
                string = key.split('_')
                o_id = string[2].split('-')[1]
                option = Option.objects.get(id=o_id)
                if ctr == 0:
                    option.option_no = value
                    ctr += 1
                else:
                    option.option = value
                    ctr -= 1
                option.save()

        return Response(request.data, status=status.HTTP_202_ACCEPTED)


class AssessmentExportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        try:
            assessment_id = request.session['assessment']
            assessment = Assessment.objects.get(id=assessment_id)
            assessment_dict = model_to_dict(assessment)
            json_data = json.dumps(assessment_dict)
            serializer = AssessmentSerializer(instance=assessment)
            question_list = list(Question.objects.filter(assessment=assessment))
            question_dict = {'type': assessment.type}
            question_data_list = []
            
            for i, q in enumerate(question_list):
                # if assessment.type == 'Multiple Choice':
                options = list(Option.objects.filter(question=q).values_list('option', flat=True))
                
                question_data = {
                    'question': q.question,
                    'options': options,
                    'answer': q.answer
                }
                
                option_answer = Option.objects.filter(question=q, option_no=question_data['answer']).values('option')
                question_data['answer'] = option_answer[0]['option']
                question_data_list.append(question_data)

            question_dict['questions'] = question_data_list
            request.session['assessment'] = assessment.pk
            
            converter = Converter()
            pdf_data = converter.quiz_to_pdf(assessment=question_dict, type=assessment.type)
            converter.quiz_answer_key(question_dict, assessment.type)
            
            return JsonResponse(question_dict, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        
        return Response(request.data, status=status.HTTP_200_OK)


