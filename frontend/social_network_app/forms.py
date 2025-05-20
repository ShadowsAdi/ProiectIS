from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Profile, CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=True)
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2100)), required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True, ip_address=None):
        user = super().save(commit=False)
        if ip_address:
            user.ip_address = ip_address
        if commit:
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = self.cleaned_data['gender']
            profile.date_of_birth = self.cleaned_data['birth_date']
            profile.save()

        return user

#asta e file-ul unde trb modificat social_network_app/login
#foloseste template-ul de la UserCreationForm si adauga email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

