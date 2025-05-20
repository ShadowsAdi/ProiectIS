from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Post, Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=True)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2100)), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            print("Profile created:", created)

            profile.gender = self.cleaned_data['gender']
            profile.date_of_birth = self.cleaned_data['birth_date']
            profile.save()

        return user
#asta e file-ul unde trb modificat social_network_app/login
#foloseste template-ul de la UserCreationForm si adauga email

MAX_FILE_SIZE = 10 * 1024 * 1024 #10 MB

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content','files','images']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['content'].required = True

    def clean_files(self): #validation method
        files = self.cleaned_data.get('files')
        print(f"clean_files received: {files} type: {type(files)}")
        if files and files.size > MAX_FILE_SIZE:
            raise ValidationError("Files should not exceed " + str(MAX_FILE_SIZE) + "MB")
        return files

    def clean_images(self):
        images = self.cleaned_data.get('images')
        print(f"clean_files received: {images} type: {type(images)}")
        if images and images.size > MAX_FILE_SIZE:
            raise ValidationError("Images should not exceed " + str(MAX_FILE_SIZE) + "MB")
        return images
