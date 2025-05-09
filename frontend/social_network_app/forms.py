from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
#asta e file-ul unde trb modificat social_network_app/login
#foloseste template-ul de la UserCreationForm si adauga email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

