from django import forms
from django.core.validators import MinValueValidator

from api.models import User, Assessment


class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'johndoe@example.com',
                                                           'label': 'Email'}),
                             required=False)
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'johndoe',
                                                             'label': 'Username'}),
                               required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'min of 8 characters',
                                                                 'label': 'Password'}),
                               required=False)


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'label': 'Email'}),
                             required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'label': 'Password'}),
                               required=False)


class AssessmentAddForm(forms.Form):
    name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Enter name'}), required=False)
    type = forms.ChoiceField(choices=Assessment.TYPE_CHOICES, widget=forms.Select(), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'label': 'description',
                                                               'placeholder': 'What is this quiz about? Give your '
                                                                              'quiz a description!'}),
                                  required=False)
    lesson = forms.CharField(
        widget=forms.Textarea(attrs={'label': 'Lesson',
                                     'placeholder': 'The material will be the source and the '
                                                    'basis of the quiz that would be generated '
                                                    'by the system. Please have a source '
                                                    'material that is descriptive and '
                                                    'comprehensive as to generate an equally '
                                                    'quality assessment.'}),
        required=False)
    no_of_questions = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of questions'}),
        required=False,
        validators=[MinValueValidator(0)]
    )
    learning_outcomes = forms.CharField(widget=forms.Textarea(attrs={'label': 'Learning Outcomes',
                                                                     'placeholder': 'Enter learning outcomes '
                                                                                    '(separate with a comma)'}))
