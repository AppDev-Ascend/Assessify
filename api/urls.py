from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserRegisterView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    

    path('home', views.AssessmentsView.as_view(), name='home'),
    path('create_assessment',views.CreateAssessmentView.as_view(), name='create_assessment'),
    path('view_assessment', views.ViewAssessmentView.as_view(), name='view_assessment'),
    path('assessment_export', views.AssessmentExportView.as_view(), name='export_assessment'),
    
    # path('assessment', views.AssessmentView.as_view(), name='assessment'),
    # path('assessment_type', views.AssessmentTypeView.as_view(), name='assessment_type'),
    # path('assessment_add', views.AssessmentAddView.as_view(), name='assessment_add'),
    # path('assessment_questions', views.AssessmentQuestionsView.as_view(), name='assessment_questions'),
]