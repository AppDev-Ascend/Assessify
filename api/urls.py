from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserRegisterView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    

    path('home', views.AssessmentsView.as_view(), name='home'),

    path('assessment_add', views.AssessmentAddView.as_view(), name='assessment_add'),
    path('assessment_questions', views.AssessmentQuestionsView.as_view(), name='assessment_questions'),
    path('assessment_export', views.AssessmentExportView.as_view(), name='assessment_export')
]