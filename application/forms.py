from django import forms
from django.contrib.auth.models import User
from models import *

class RegistrationForm(forms.Form):
    fname = forms.CharField(max_length = 20,
            widget=forms.TextInput(attrs={'class':'form-control',
                'name':'fname','placeholder':'First Name'}))
    lname = forms.CharField(max_length = 20,
            widget=forms.TextInput(attrs={'class':'form-control',
                'name':'lname','placeholder':'Last Name'}))
    username = forms.CharField(max_length = 20,
            widget=forms.TextInput(attrs={'class':'form-control',
                'name':'username','placeholder':'Username'}))

    email = forms.EmailField(max_length = 200,
            widget=forms.TextInput(attrs={'class':'form-control',
                'name':'email', 'placeholder':'Email'}))
    password1 = forms.CharField(max_length=200, 
            label='Password',
            widget = forms.PasswordInput(attrs={
                'class':'form-control', 'name':'password1',
                'placeholder':'Password'}))
    password2 = forms.CharField(max_length=200,
            label='Confirm Password',
            widget= forms.PasswordInput(attrs={
                'class':'form-control', 'name':'password2',
                'placeholder':'Confirm Password'}))
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not Match")

        username = cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username already exists")

        return cleaned_data
        
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = ('answered', 'date', 'responses', 'user', 'votes', )
        widgets = {'picture' : forms.FileInput()} 

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        exclude = ('user', 'votes', 'request', 'selected_answer', 'request', 'comments', )
        widgets = {'picture' : forms.FileInput()} 

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'votes', 'request', 'response', )

class AppUserForm(forms.ModelForm):
    class Meta:
        model=AppUser
        exclude = ('votes_for', 'user', 'requests', 'points', 'last_name',
        'followed_users', 'first_name','expertise',)
        widgets={'picture' : forms.FileInput()}
