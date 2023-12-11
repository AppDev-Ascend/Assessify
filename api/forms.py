from django import forms
from django.core.validators import MinValueValidator
from django.forms import formset_factory

from .models import Learning_Outcomes, Question_Type, Section, User, Assessment, Question, Option


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'min of 8 characters', 'label': 'Password'}), required=True)
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter password to confirm password.'}), required=True)

    class Meta:
        model = User
        fields = ('email', 'username')
        widgets = {
            'email': forms.TextInput(),
            'username': forms.TextInput(),
        }
 
class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(required=True)
    
class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = (
            'name',
            'type',
            'description',
            'lesson',
            'no_of_questions',
        )
        widgets = {
            'name': forms.TextInput(attrs={'disabled': 'disabled'}),
            'type': forms.TextInput(attrs={'disabled': 'disabled'}),
            'description': forms.Textarea(attrs={'disabled': 'disabled'}),
            'lesson': forms.TextInput(attrs={'disabled': 'disabled'}),
            'no_of_questions': forms.NumberInput(attrs={'disabled': 'disabled'}),
        }

class AssessmentAddForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter name'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'What is this quiz about? Give your '
                                     'quiz a description!', 'rows': 2})
    )
    lesson = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Type your Lesson here', 'rows': 10}),
        required=False
    )
    file = forms.FileField(
        widget=forms.FileInput(), 
        label='Lesson File', 
        required=False
    )
    no_of_questions = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of questions'})
    )
    learning_outcomes = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter learning outcomes '
                                     '(separate with a comma)'}),
        label='Learning Outcomes'
    )
    question_type = forms.ModelChoiceField(
        queryset=Question_Type.objects.all(),
        widget=forms.Select(attrs={'label': 'Question Type'}),
        label="Question Type",
        to_field_name="name"
    )

class AssessmentSectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ('section_no', 'type')

class LearningOutcomeForm(forms.ModelForm):
    class Meta:
        model = Learning_Outcomes
        fields = ('learning_outcome',)
        

class AssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question_no', 'question', 'answer')
        widgets = {
            'question_no': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class AssessmentOptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_no', 'option']




