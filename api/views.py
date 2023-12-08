import json
import os
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend


from .validations import login_validation, register_validation, validate_assessment
from .forms import RegisterForm, LoginForm, AssessmentAddForm, AssessmentQuestionForm, AssessmentOptionForm
from .converter import Converter
from .models import Assessment, User, Question, Option
from .file_handler import handle_uploaded_file, handle_non_utf8

from django.views.generic.base import View

# Notes:
# permission_classes - specifies what kind of user can enter the view
# authentication_classes - requires authentication to enter the view specifically the presence of the sessionid
# return Response() - returns a dictionary in json

class UserRegisterView(View):
    def get(self, request):

        if request.user.is_authenticated:
            return redirect('home')

        template = "api/register.html"
        form = RegisterForm()
        return render(request, template, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            re_password = form.cleaned_data['re_password']

            if password == re_password:
                user = form.save()
                login(request, user)
                return redirect('home')
            else:
                form.add_error('re_password', 'Passwords do not match.')
        else:
            print(form.errors)
        return render(request, 'api/register.html', {'form': form})

class UserLoginView(View):
    def get(self, request):

        if request.user.is_authenticated:
            return redirect('home')

        template = "api/login.html"
        form = LoginForm()
        return render(request, template, {'form': form})
    
    def post(self, request):
        try:
            validated_data = login_validation(request.POST)
            user = authenticate(request, 
                                email=validated_data['email'],
                                password=validated_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                raise ValidationError("Incorrect username or password")
        except ValidationError as e:
            return render(request, 'api/login.html', {'form': LoginForm(), 'error': e.message})

class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('register')

@method_decorator(login_required, name='dispatch')
class AssessmentsView(View):

    def get(self, request):
        assessments = Assessment.objects.filter(user_id=request.user.user_id)
        template = "api/homepage.html"
        return render(request, template, {'assessments': assessments})


# Adds assessments
@method_decorator(login_required, name='dispatch')
class AssessmentAddView(View):
    # Modify here for front-end
    def get(self, request):
        # Currently for testing
        template = "api/assessment_add.html"
        form = AssessmentAddForm()
        return render(request, template, {'form': form})

    def post(self, request):
        try:
            data_copy = request.POST.copy()
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
        


@method_decorator(login_required, name='dispatch')
class AssessmentQuestionsView(View):
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


@method_decorator(login_required, name='dispatch')
class AssessmentExportView(View):
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

            with open('question_dict.json', 'w') as f:
                json.dump(question_dict, f)


            pdf_data = Converter.quiz_to_pdf(assessment=question_dict, type=assessment.type)
            Converter.quiz_answer_key(assessment=question_dict, type=assessment.type)
            
            return JsonResponse(question_dict, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


