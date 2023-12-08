from django import forms
from django.core.validators import MinValueValidator
from django.forms import formset_factory

from .models import User, Assessment, Question, Option


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'min of 8 characters', 'label': 'Password'}))
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter password to confirm password.'}))

    class Meta:
        model = User
        fields = ['email', 'username']
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'johndoe@example.com', 'label': 'Email'}),
            'username': forms.TextInput(attrs={'placeholder': 'johndoe', 'label': 'Username'}),
        }

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'johndoe@example.com'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'min of 8 characters'})
        }


class AssessmentAddForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter name'}))
    type = forms.ChoiceField(choices=Assessment.TYPE_CHOICES, widget=forms.Select())
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'What is this quiz about? Give your '
                                                               'quiz a description!', 'rows': 2}))
    lesson = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your Lesson here', 'rows': 10}),
                             required=False)
    file = forms.FileField(widget=forms.FileInput(), label='Lesson File', required=False)
    no_of_questions = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Enter number of questions'}))
    learning_outcomes = forms.CharField(widget=forms.Textarea(attrs={'label': 'Learning Outcomes',
                                                                     'placeholder': 'Enter learning outcomes '
                                                                                    '(separate with a comma)'}))
    
class AssessmentQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_no', 'question', 'answer']
        widgets = {
            'question_no': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class AssessmentOptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_no', 'option']




