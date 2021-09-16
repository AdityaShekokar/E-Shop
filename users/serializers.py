from django.contrib.auth.forms import UserCreationForm
from django.forms import forms
from rest_framework import serializers
from rest_framework.response import Response

from users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    passWord = serializers.CharField(source="password")

    class Meta:
        model = User
        fields = ["firstName", "lastName", "email", "passWord"]

    def create(self, data):
        data.update({"username": data.get("email")})
        return User.objects.create_user(**data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    passWord = serializers.CharField()

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(
#         max_length=100,
#         required=True,
#         help_text='Enter Email Address',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#     )
#     first_name = forms.CharField(
#         max_length=100,
#         required=True,
#         help_text='Enter First Name',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'},
#         source="first_name"),
#     )
#     last_name = forms.CharField(
#         max_length=100,
#         required=True,
#         help_text='Enter Last Name',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
#     )
#     username = forms.CharField(
#         max_length=200,
#         required=True,
#         help_text='Enter Username',
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
#     )
#     password1 = forms.CharField(
#         help_text='Enter Password',
#         required=True,
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
#     )
#     password2 = forms.CharField(
#         required=True,
#         help_text='Enter Password Again',
#         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again'}),
#     )
#     check = forms.BooleanField(required=True)
#
#     class Meta:
#         model = User
#
#     fields = [
#         'username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'check',
#     ]
