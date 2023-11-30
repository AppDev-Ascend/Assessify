import json
import urllib

from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import RegisterForm, LoginForm, AssessmentAddForm
from .models import User
from .serializers import UserRegisterSerializer, UserLoginSerializer, AssessmentsSerializer, AssessmentAddSerializer
from rest_framework import permissions, status


# Notes:
# permission_classes - specifies what kind of user can enter the view
# authentication_classes - requires authentication to enter the view specifically the presence of the sessionid
# return Response() - returns a dictionary in json

class UserRegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    # Modify for front-end here
    def get(self, request):
        # Currently for testing
        template = "api/register.html"
        form = RegisterForm()
        return render(request, template, {'form': form})

    # Returns a dictionary of the registered user
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

    # Redirects to homepage after logging in
    def post(self, request):
        try:
            data = request.data
            serializer = UserLoginSerializer(data)
            user = serializer.check_user(data)
            login(request, user)
            return redirect(reverse('homepage'))
        except ValidationError as e:
            # Modify front-end here
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)


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

    # Modify here for front-end
    def get(self, request):
        # Currently for testing
        template = "api/assessment_add.html"
        form = AssessmentAddForm()
        return render(request, template, {'form': form})

    # Returns dictionary of the newly added Assessment
    def post(self, request):
        try:
            data = request.data.copy()
            user_id = request.session['_auth_user_id']
            user = User.objects.get(pk=user_id)
            data['user'] = user
            serializer = AssessmentAddSerializer(data)
            serializer.create(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)