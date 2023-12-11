from http.client import HTTPResponse
import json
import mimetypes
import os
from zipfile import ZipFile
from urllib.parse import unquote, urlencode
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

from api.backends import CustomEmailBackend


from .validations import login_validation, register_validation, validate_assessment
from .forms import AssessmentForm, RegisterForm, LoginForm, AssessmentAddForm, AssessmentQuestionForm, AssessmentOptionForm
from .converter import Converter
from .models import Assessment, Question_Type, User, Question, Option
from .file_handler import download_file, handle_uploaded_file, handle_non_utf8

from django.views.generic.base import View


# Notes:
# permission_classes - specifies what kind of user can enter the view
# authentication_classes - requires authentication to enter the view specifically the presence of the sessionid
# return Response() - returns a dictionary in json

class UserRegisterView(View):
    template = "api/register.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template)

    def post(self, request):
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        re_password = request.POST.get('repassword')
        error = ''
        
        if password == re_password:
            user = User.objects.create_user(email=email,
                                            username=username, 
                                            password=password)
            if user is not None:
                return redirect('home')
            else:
                error = 'Email already existing'
        else:
            error = 'Incorrect password'
        return render(request, self.template, {'error': error})

class UserLoginView(View):
    template = "api/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        return render(request, self.template)

    def post(self, request):
        error = ''
        
        user = authenticate(
            request,
            email=request.POST.get('email'),
            password=request.POST.get('password'),
            backend='api.backends.CustomEmailBackend'
        )
        
        if user is not None:
            
            login(request, user)
            return redirect('home')
        else:
            error = 'Incorrect email or password'
            
        return render(request, self.template, {'error': error})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

@method_decorator(login_required, name='dispatch')
class AssessmentsView(View):
    template = "api/dashboard.html"

    def get(self, request):
        user_id = request.session['_auth_user_id']
        user = User.objects.get(user_id=user_id)
        assessments = Assessment.objects.filter(user_id=request.user.user_id)
        return render(request, self.template, {'user': user, 'assessments': assessments})
    
    def post(self, request):
        return 
    
@method_decorator(login_required, name='dispatch')
class AssessmentView(View):
    template = 'api/assessment.html'
    
    def get(self, request):
        action = request.GET.get('act')    
        print(action)    
        assessment_name = request.GET.get('as')
        assessment = Assessment.objects.get(name=assessment_name)
        a_form = AssessmentForm(instance=assessment)
        
        form_list = []
        section_list = Section
        questions = Question.objects.filter(assessment_id=assessment.pk)
        q_list = list(questions)
        if assessment.type == 'quiz':
            q_type.append(questions.type[0])
        # elif assessment.type == 'exam':
            
        for q in q_list:
            q_form = AssessmentQuestionForm(instance=q)
            q_form.prefix = f'question_{q.pk}_content'  # Set a unique prefix for each question form
            form_list.append(q_form)

            options = Option.objects.filter(question_id=q.pk)
            o_list = list(options)
            for o in o_list:
                o_form = AssessmentOptionForm(instance=o)
                o_form.prefix = f'option_q-{q.pk}_o-{o.pk}_content'  # Set a unique prefix for each option form
                form_list.append(o_form)
        
        view = False
        if action == 'view':
            view = True
            for field_name, field in a_form.fields.items():
                field.widget.attrs['disabled'] = 'disabled'
            
            for form in form_list:
                for field_name, field in form.fields.items():
                    field.widget.attrs['disabled'] = 'disabled'
            
        return render(request, self.template, {'assessment': assessment,
                                               'a_form': a_form, 
                                               'q_type': q_type,
                                               'form_list': form_list,
                                               'view': view})

    def post(self, request):
        action = request.GET.get('act')    
        assessment_name = request.GET.get('as')
        assessment = Assessment.objects.get(name=assessment_name)
        ctr = 0
        
        if action == 'edit':
            for key, value in request.POST.items():
                print(f'Key: {key}, Value: {value}')
                if key.startswith('question_'):
                    string = key.split('_')
                    q_id = int(string[1])
                    qc = string[2].split('-')[1]
                    question = Question.objects.get(id=q_id)

                    if qc == "question_no":
                        question.question_no = value
                    elif qc == "question":
                        question.question = value
                    elif qc == "answer":
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
            return redirect(reverse('assessment_view') + '?' + urlencode({'as': assessment_name, 'act': 'view'}))
        
        file_format = request.POST.get('formats')    
        return redirect(reverse('assessment_export') + '?' + urlencode({'as': assessment_name, 'ff': file_format}))

@method_decorator(login_required, name='dispatch')
class AssessmentTypeView(View):
    def get(self, request):
        template = "api/assessment_type.html"
        return render(request, template)

@method_decorator(login_required, name='dispatch')
class CreateAssessmentView(View):
    template = 'api/create_assessment.html'
    
    def get(self, request):
        a_type = request.GET.get('type')
        print(a_type)
        return render(request, self.template)

    def post(self, request):
        form = AssessmentAddForm(request.POST)
        user_id = request.session['_auth_user_id']
        user = User.objects.get(pk=user_id)
        a_type = request.GET.get('at')
        
        if form.is_valid():
            if 'file' in request.FILES:
                file = request.FILES['file']
                path = os.path.join(settings.MEDIA_ROOT, 'files', file.name)
                handle_uploaded_file(file)
                file_format = file.name.split('.')[1].lower()
                
                # pdf to text convert
                if file_format == 'pdf':
                    lesson = Converter.pdf_to_text(path)
                
            else:
                lesson = form.cleaned_data['lesson']
                print('no file')
        
        assessment = Assessment.objects.create(name=form.cleaned_data['name'],
                                               type=a_type,
                                               description=form.cleaned_data['description'],
                                               lesson=lesson,
                                               no_of_questions=form.cleaned_data['no_of_questions'],
                                               learning_outcomes=form.cleaned_data['learning_outcomes'],
                                               user=user)
        
        q_type = form.cleaned_data['question_type']
        
        if a_type == 'quiz':
            assessment.create_quiz(q_type=q_type)
        elif a_type == 'exam':
            assessment.create_exam(q_type=q_type)
        
        return redirect(reverse('assessment_questions') + '?' + urlencode({'as': assessment.name, 'qt': q_type}))

# Adds assessments
@method_decorator(login_required, name='dispatch')
class AssessmentAddView(View):
    # Modify here for front-end
    def get(self, request):
        template = "api/assessment_add.html"
        form = AssessmentAddForm()
        a_type = request.GET.get('at')
        # if a_type == 'quiz':
            
        return render(request, template, {'form': form})

    def post(self, request):
        form = AssessmentAddForm(request.POST)
        user_id = request.session['_auth_user_id']
        user = User.objects.get(pk=user_id)
        a_type = request.GET.get('at')
        
        if form.is_valid():
            if 'file' in request.FILES:
                file = request.FILES['file']
                path = os.path.join(settings.MEDIA_ROOT, 'files', file.name)
                handle_uploaded_file(file)
                file_format = file.name.split('.')[1].lower()
                
                # pdf to text convert
                if file_format == 'pdf':
                    lesson = Converter.pdf_to_text(path)
                
            else:
                lesson = form.cleaned_data['lesson']
                print('no file')
        
        assessment = Assessment.objects.create(name=form.cleaned_data['name'],
                                               type=a_type,
                                               description=form.cleaned_data['description'],
                                               lesson=lesson,
                                               no_of_questions=form.cleaned_data['no_of_questions'],
                                               learning_outcomes=form.cleaned_data['learning_outcomes'],
                                               user=user)
        
        q_type = form.cleaned_data['question_type']
        
        if a_type == 'quiz':
            assessment.create_quiz(q_type=q_type)
        elif a_type == 'exam':
            assessment.create_exam(q_type=q_type)
        
        return redirect(reverse('assessment_questions') + '?' + urlencode({'as': assessment.name, 'qt': q_type}))
        
@method_decorator(login_required, name='dispatch')
class AssessmentQuestionsView(View):
    template_name = 'api/assessment_question.html'
    
    def get(self, request):
        assessment_name = request.GET.get('as')
        assessment = Assessment.objects.get(name=assessment_name)
        q_type = request.GET.get('qt')
        questions = Question.objects.filter(assessment=assessment)
        q_list = list(questions)
        form_list = []

        for q in q_list:
            q_form = AssessmentQuestionForm(instance=q)
            # print(q.pk)
            q_form.prefix = f'question_{q.pk}_content'  # Set a unique prefix for each question form
            form_list.append(q_form)

            options = Option.objects.filter(question_id=q.pk)
            o_list = list(options)
            for o in o_list:
                o_form = AssessmentOptionForm(instance=o)
                o_form.prefix = f'option_q-{q.pk}_o-{o.pk}_content'  # Set a unique prefix for each option form
                form_list.append(o_form)

        return render(request, template_name=self.template_name, context={'form_list': form_list, 'assessment': assessment, 'q_type': q_type})

    
    def post(self, request):    
        ctr = 0
        for key, value in request.POST.items():
            # print(f'Key: {key}, Value: {value}')
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

        action = request.POST.get('action')
        assessment_name = request.GET.get('as')
        q_type = request.GET.get('qt')
        print(q_type)
        print(assessment_name)
            
        return redirect('home')
            
    
@method_decorator(login_required, name='dispatch')
class AssessmentExportView(View):
    
    def get(self, request):
        assessment_name = request.GET.get('as')
        q_type = request.GET.get('qt')
        file_format = request.GET.get('ff')
        assessment = Assessment.objects.get(name=assessment_name) 
        question_list = list(Question.objects.filter(assessment=assessment))
        question_dict = {'type': q_type}
        question_data_list = []
        
        for i, q in enumerate(question_list):
            options = list(Option.objects.filter(question=q).values_list('option', flat=True))
            
            question_data = {
                'question': q.question,
                'options': options,
                'answer': q.answer
            }
            
            option_answer = Option.objects.filter(question=q, option_no=q.answer).values('option').first()
            question_data['answer'] = option_answer['option']
            question_data_list.append(question_data)

        question_dict['questions'] = question_data_list

        with open('question_dict.json', 'w') as f:
            json.dump(question_dict, f)

        file_path = rf'files\exports\{assessment_name}.zip'
        
        if file_format == 'pdf':
            Converter.quiz_to_pdf(assessment=question_dict, type=q_type, name=assessment_name)
            Converter.quiz_answer_key(assessment=question_dict, type=q_type, name=assessment_name)
        
        with ZipFile(rf'{settings.MEDIA_ROOT}\files\exports\{assessment_name}.zip', 'w') as zip_object:
            # Adding files that need to be zipped
            if assessment.type == 'quiz':
                quiz_file_path = rf'{settings.MEDIA_ROOT}\files\exports\quiz_{assessment.name}.{file_format}'
                answer_key_file_path = rf'{settings.MEDIA_ROOT}\files\exports\quiz_answer_key_{assessment.name}.{file_format}'
                
                zip_object.write(quiz_file_path, os.path.basename(quiz_file_path))
                zip_object.write(answer_key_file_path, os.path.basename(answer_key_file_path))
        
        return download_file(request, rf'files\exports\{assessment_name}.zip')

