from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import AssessmentAddForm, AssessmentQuestionForm, AssessmentOptionForm
from .models import User, Question, Option
from .serializers import UserRegisterSerializer, UserLoginSerializer, AssessmentsSerializer, AssessmentAddSerializer, \
    AssessmentQuestionSerializer
from rest_framework import permissions, status
from django.contrib.auth import authenticate

# Notes:
# permission_classes - specifies what kind of user can enter the view
# authentication_classes - requires authentication to enter the view specifically the presence of the sessionid
# return Response() - returns a dictionary in json

class UserRegisterView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = []

    """
    {
        "email": "testadmin1",
        "password": "admin1234"
    }
    """

    # Returns a dictionary of the registered user
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Creates a sessionid when successfully logged in
class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.check_user(serializer.validated_data)
            login(request, user)
            return Response({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'is_authenticated': user.is_authenticated,
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Needs the logout() method to terminate the sessionid
class UserLogoutView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class HomePageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # Modify this for front-end
    def get(self, request):
        # Currently for testing
        # serializer = UserSerializer(request.user)
        return Response(request.session, status=status.HTTP_200_OK)


# List of Assessments page
# Uses session['_auth_user_id'] to get user_id
class AssessmentsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # Returns a dictionary of a list of assessments
    def get(self, request):
        user_id = request.session['_auth_user_id']
        assessments = AssessmentsSerializer()
        data = assessments.get_assessments(user_id)
        return Response(data, status=status.HTTP_200_OK)


# Adds assessments
# Uses session['_auth_user_id'] to get user_id
class AssessmentAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    # # Modify here for front-end
    # def get(self, request):
    #     # Currently for testing
    #     template = "api/assessment_add.html"
    #     form = AssessmentAddForm()
    #     return render(request, template, {'form': form})


    # Json format
    # {
    #     name: "",
    #     type: "",
    #     description: "",
    #     lesson: "",
    #     no_of_questions: 5,
    #     learn_outcomes: "",
    # }

    # Returns dictionary of the Assessment
    def post(self, request):
        try:
            data = request.data.copy()
            user_id = request.session['_auth_user_id']
            user = User.objects.get(pk=user_id)
            data['user'] = user
            serializer = AssessmentAddSerializer(data)
            questions = serializer.create(data)
            request.session['assessment'] = questions['assessment']
            return redirect(reverse('assessment_questions'))
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)


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


class ExportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        return Response(request.data, status=status.HTTP_200_OK)

    def post(self, request):
        return Response(request.data, status=status.HTTP_200_OK)
