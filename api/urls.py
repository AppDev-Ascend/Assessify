from django.urls import path
from . import views

urlpatterns = [
    path('register', views.UserRegisterView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),  # can remove this for front-end
    path('homepage', views.HomePageView.as_view(), name='homepage'),
    path('assessments', views.AssessmentsView.as_view(), name='assessments'),
    path('assessment_add', views.AssessmentAddView.as_view(), name='assessment_add'),
]