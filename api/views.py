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
from django.db.utils import IntegrityError


from django.contrib.auth import authenticate, login


from .validations import login_validation, register_validation, validate_assessment
from .forms import AssessmentForm, RegisterForm, LoginForm, AssessmentAddForm, AssessmentQuestionForm, AssessmentOptionForm
from .converter import Converter
from .models import Assessment, Question_Type, User, Question, Option, Section
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
            try:
                user = User.objects.create_user(email=email, username=username, password=password)
                # If the user is created successfully, you can redirect
                return redirect('home')
            
            except IntegrityError as e:
                if 'email' in str(e):
                    error = 'Email already exists'
                else:
                    error = 'Username already exists'
                
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
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if '@' in email and '.com' in email:
            user = authenticate(
                request,
                email=email,
                password=password,
            ) 
        
        else:
            user = authenticate(
                request,
                username=email, 
                password=password,
            )
 
        if user is not None:
            login(request, user)
            return redirect('home')
        
        else:
            error = 'Incorrect username/email or password'
            
        return render(request, self.template, {'error': error})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

@method_decorator(login_required, name='dispatch')
class CreateAssessmentView(View):
    template = 'api/create_assessment.html'
    
    def get(self, request):
        a_type = request.GET.get('type')
        print(a_type)
        return render(request, self.template)

    def post(self, request):
        user_id = request.session['_auth_user_id']
        user = User.objects.get(pk=user_id)
        print(f'user: {user_id}')
        
        # for assessment creation
        assessment_name = request.POST.get('assessment_name')
        assessment_description = request.POST.get('assessment_description')
        lesson = request.POST.get('lesson')
        assessment_type = request.GET.get('type')
        no_of_questions = 0
        
        # for quiz/exam creation parameters
        section = {}
        section_types = []
        section_lengths = []
        learning_outcomes = []
        # no_of_sections = 0
        
        if assessment_type == 'quiz':
            # no_of_sections = 1
            for key, value in request.POST.items():
                print(f'KEY: {key}, VALUE: {value}')
                
                if key.startswith('section-type'):
                    section_types.append(value.lower().lstrip())

                elif key.startswith('section-length'):
                    num = int(value.split(' ')[0])
                    section_lengths.append(num)
                    no_of_questions += num
                
                elif key.startswith('learning-outcomes'):
                    learning_outcomes.append(value)
        
        elif assessment_type == 'exam':
            s = []
            for key, value in request.POST.items():
                print(f'key: {key}')
                print(f'value: {value}')
                
                if key.startswith('section-type'):
                    # no_of_sections += 1
                    s = []
                    section_types.append(value.lower().lstrip())
                
                elif key.startswith('section-length'):
                    num = int(value.lstrip().split(' ')[0])
                    section_lengths.append(num)
                    no_of_questions += num
                
                elif key.startswith('learning-outcomes'):
                    if not s:
                        learning_outcomes.append(s)
                    s.append(value)
            
            print(f's_types: {section_types}')
            print(f's_lengths: {section_lengths}')
            print(f'l_outcomes: {learning_outcomes}')
                            
        if 'lesson_file' in request.FILES:
            file = request.FILES['lesson_file']
            file_name = f'{user_id}_{file.name}'
            path = os.path.join(settings.MEDIA_ROOT, 'files', file_name)
            handle_uploaded_file(file, file_name)
            file_format = file.name.split('.')[1].lower()
            
            # pdf to text convert
            if file_format == 'pdf':
                lesson = Converter.pdf_to_text(path)
            
        else:
            print('no file')

        # assign the necessary values to the section dictionary
        section['section_types'] = section_types
        section['section_lengths'] = section_lengths
        section['learning_outcomes'] = learning_outcomes
        
        assessment = Assessment.objects.create(name=assessment_name,
                                               type=assessment_type,
                                               description=assessment_description,
                                               lesson=lesson,
                                               no_of_questions=no_of_questions,
                                               user=user)
        print(f'assessment_id: {assessment.pk}')
        
        if assessment_type == 'quiz':
            assessment.create_quiz(section)
        elif assessment_type == 'exam':
            assessment.create_exam(section)
        
        return redirect(reverse('view_assessment') + '?' + urlencode({'as': assessment.pk, 'page': 'view'}))

@method_decorator(login_required, name='dispatch')
class ViewAssessmentView(View):
    template = 'api/assessment_viewer.html'
    
    # view assessment generated
    def get(self, request):
        action = request.GET.get('page')
        assessment_id = request.GET.get('as')
        assessment = Assessment.objects.get(id=assessment_id)
        sections = list(Section.objects.filter(assessment=assessment))
        question_types = []
        
        question_group = []
        question_group_attrs = {
            'question': Question,
            'options': list
        }
        QuestionGroup = type('QuestionGroup', (object,), question_group_attrs)
        
        for s in sections:
            qt = Question_Type.objects.get(id=s.type_id)
            question_types.append(qt)
            questions = list(Question.objects.filter(section=s).order_by('question_no'))
            q_list = []
            
            for q in questions:
                
                # when true or false includes options
                # if qt.type == 'Multiple Choice' or qt.type == 'True or False':
                if qt.type == 'Multiple Choice':
                    options = list(Option.objects.filter(question=q).order_by('option_no'))
                    
                    for i, o in enumerate(options, start=1):
                        # reassigns the answer of the question to its 
                        # letter equivalent + worded answer
                        if q.answer == str(i):
                            q.answer = f"{chr(ord('A') + i - 1)}. {o.option}"
                       
                temp_question_group = QuestionGroup()
                temp_question_group.question = q
                temp_question_group.options = options
                print(f'question: {q}')
                print(f'answer: {q.answer}')
                q_list.append(temp_question_group)    
                
            question_group.append(q_list)  
                
        
        # assessment = assessment object
        # sections = the sections in the assessment
        # question_types = question type of each section
        # question_groups = questions, answers, options of each section 
        assessment_data = zip(sections, question_types, question_group)
        
        return render(request, self.template, context={'action': action,
                                                       'assessment': assessment,
                                                       'assessment_data': assessment_data})
        
    # edit assessment generated
    def post(self, request):
        assessment_id = request.GET.get('as')
        for key, value in request.POST.items():
            print(f'key: {key}')
            print(f'value: {value}')
            k = key.split('_')
            
            if k[0] == 'assessmentname':
                assessment = Assessment.objects.get(pk=k[1])
                assessment.name = value
                assessment.save()
                
            elif k[0] == 'assessmentdescription':
                assessment = Assessment.objects.get(pk=k[1])
                assessment.description = value
                assessment.save()
            
            elif k[0] == 'sectiondescription':
                section = Section.objects.get(pk=k[1])
                section.description = value
                section.save()
            
            elif k[0] == 'question':
                question = Question.objects.get(pk=k[1])
                question.question = value
                question.save()
            
            elif k[0] == 'answerwc':
                question = Question.objects.get(pk=k[1])
                # converts the letter to the number equivalent
                number = ord(value.split('.')[0]) - ord('A') + 1
                question.answer = number
                question.save()
                
            elif k[0] == 'answer':
                question = Question.objects.get(pk=k[1])
                question.answer = value
                question.save()
            
            elif k[0] == 'option':
                option = Option.objects.get(pk=k[1])
                option.option = value
                option.save()
            
        return redirect(reverse('view_assessment') + '?' + urlencode({'as': assessment_id, 'page': 'view'}))

# exports assessment        
@method_decorator(login_required, name='dispatch')
class AssessmentExportView(View):
    
    def get(self, request):
        user_id = request.session['_auth_user_id']
        username = User.objects.get(user_id=user_id).username
        assessment_id = request.GET.get('as')
        file_format = request.GET.get('ff')
        assessment = Assessment.objects.get(id=assessment_id)
        sections = Section.objects.filter(assessment=assessment)
        
        if assessment.type == 'quiz':
            sec = sections[0]
            type = sec.type.type
            question_list = list(Question.objects.filter(section=sec))
            question_dict = {'type': type}
            question_data_list = []
            
            for q in question_list:
                question_data = {
                    'question': q.question,
                    'answer': q.answer
                }
                
                if type == 'Multiple Choice':
                    # gets the list of data from the column 'option'
                    options = list(Option.objects.filter(question=q).values_list('option', flat=True))
                    question_data['options'] = options
                    option_answer = Option.objects.get(question=q, option_no=q.answer)
                    question_data['answer'] = f'{chr(96 + option_answer.option_no)}. {option_answer}'
                    
                question_data_list.append(question_data)   
                
            question_dict['questions'] = question_data_list
            
            with open('question_dict.json', 'w') as f:
                json.dump(question_dict, f)
            
            if file_format == 'pdf':
                Converter.quiz_to_pdf(assessment=question_dict, type=type, name=assessment.name)
                Converter.quiz_answer_key(assessment=question_dict, type=type, name=assessment.name)
                """
                if there is a custom file naming convention
                
                Converter.quiz_to_pdf(assessment=question_dict,
                                      username=username, 
                                      assessment_id=assessment_id, 
                                      type=type, 
                                      assessment_name=assessment.name)
                Converter.quiz_answer_key(assessment=question_dict,
                                          username=username, 
                                          assessment_id=assessment_id, 
                                          type=type, 
                                          assessment_name=assessment.name)
                """
            elif file_format == 'gift':
                Converter.quiz_to_gift(json_data=question_dict, name=assessment.name)
        
        else:
            exam_dict = {'type': 'exam'}
            section_list = []
            
            for s in sections:
                type = s.type.type
                section_data = {
                    'section_name': s.name, 
                    'section_description': s.description, 
                    'section_type': type
                }
                question_list = list(Question.objects.filter(section=s))
                question_data_list = []
                
                for q in question_list:
                    question_data = {
                        'question': q.question,
                        'answer': q.answer
                    }
                    
                    if type == 'Multiple Choice':
                        # gets the list of data from the column 'option'
                        options = list(Option.objects.filter(question=q).values_list('option', flat=True))
                        question_data['options'] = options
                        option_answer = Option.objects.get(question=q, option_no=q.answer)
                        question_data['answer'] = f'{chr(96 + option_answer.option_no)}. {option_answer}'
                        
                    question_data_list.append(question_data)   
                
                section_data['questions'] = question_data_list
                section_list.append(section_data)

            exam_dict['sections'] = section_list
            print(exam_dict)
            
            with open('exam_dict.json', 'w') as f:
                json.dump(exam_dict, f)
            
            if file_format == 'pdf':
                Converter.exam_to_pdf(exam=exam_dict, name=assessment.name)
                Converter.exam_answer_key(exam=exam_dict, name=assessment.name)
                """
                if there is custom file naming convention
                Converter.exam_to_pdf(exam=exam_dict, 
                                      username=username, 
                                      assessment_id=assessment_id, 
                                      assessment_name=assessment.name)
                Converter.exam_answer_key(exam=exam_dict, 
                                          username=username, 
                                          assessment_id=assessment_id, 
                                          assessment_name=assessment.name)
                """
            elif file_format == 'gift':
                Converter.exam_to_gift(exam=exam_dict, output_file=None, name=assessment.name)

        
        if file_format != 'gift':
            # Create the zip file
            file_path = rf'files\exports\{assessment.name}_assessment.zip'
            
            with ZipFile(rf'{settings.MEDIA_ROOT}\{file_path}', 'w') as zip_object:
                # Adding files to the zip file
                assessment_file_name = ''
                answer_key_file_name = ''
                    
                if assessment.type == 'quiz':
                    assessment_file_name = 'quiz'
                    answer_key_file_name = 'quiz_answer-key'
                
                elif assessment.type == 'exam':
                    assessment_file_name = 'exam'
                    answer_key_file_name = 'exam_answer-key'
                
                assessment_file_path = rf'{settings.MEDIA_ROOT}\files\exports\{assessment.name}_{assessment_file_name}.{file_format}'
                answer_key_file_path = rf'{settings.MEDIA_ROOT}\files\exports\{assessment.name}_{answer_key_file_name}.{file_format}'
                        
                zip_object.write(assessment_file_path, os.path.basename(assessment_file_path))
                zip_object.write(answer_key_file_path, os.path.basename(answer_key_file_path))
                                
        else:
            file_path = rf'{settings.MEDIA_ROOT}\files\exports\{assessment.name}_{assessment.type}-gift.txt'
                        
        return download_file(request, file_path)

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

""""
            ! OLD VIEWS !
@method_decorator(login_required, name='dispatch')
class AssessmentView(View):
    template = 'api/assessment.html'
    
    def get(self, request):
        action = request.GET.get('act')    
        print(action)    
        assessment_name = request.GET.get('as')
        assessment = Assessment.objects.get(name=assessment_name)
        # a_form = AssessmentForm(instance=assessment)
        
        # form_list = []
        # section_list = Section
        # questions = Question.objects.filter(assessment_id=assessment.pk)
        # q_list = list(questions)
        # if assessment.type == 'quiz':
        #     q_type.append(questions.type[0])
        # elif assessment.type == 'exam':
            
        # for q in q_list:
        #     q_form = AssessmentQuestionForm(instance=q)
        #     q_form.prefix = f'question_{q.pk}_content'  # Set a unique prefix for each question form
        #     form_list.append(q_form)

        #     options = Option.objects.filter(question_id=q.pk)
        #     o_list = list(options)
        #     for o in o_list:
        #         o_form = AssessmentOptionForm(instance=o)
        #         o_form.prefix = f'option_q-{q.pk}_o-{o.pk}_content'  # Set a unique prefix for each option form
        #         form_list.append(o_form)
        
        # view = False
        # if action == 'view':
        #     view = True
        #     for field_name, field in a_form.fields.items():
        #         field.widget.attrs['disabled'] = 'disabled'
            
        #     for form in form_list:
        #         for field_name, field in form.fields.items():
        #             field.widget.attrs['disabled'] = 'disabled'
            
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
"""
    

