from django.contrib.auth.forms import UserCreationForm
from django.forms import forms
from rest_framework import serializers
from rest_framework.response import Response

from e_shop.common import PublicId
from users.models import Roles, Scopes, User


class RegistrationSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    passWord = serializers.CharField(source="password")
    role = serializers.CharField()

    class Meta:
        model = User
        fields = ["firstName", "lastName", "email", "passWord", "role"]

    def create(self, data):
        data.update({"username": data.get("email"), "public_id": PublicId.create_public_id()})
        roles = data.pop("role")
        user = User.objects.create_user(**data)
        for role in roles:
            role.user.add(user)
        role.save
        return user

    def validate_role(self, value):
        """
        Check that the blog post is about Django.
        """
        try:
            instances = []
            for role in value.split(","):
                query_filter = role.strip()
                role = Roles.objects.get(name__icontains=query_filter)
                instances.append(role)
            return instances
        except Roles.DoesNotExist:
            raise serializers.ValidationError({"error": f"Role '{query_filter}' does not exist."})


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


class RoleSerializer(serializers.ModelSerializer):
    publicId = serializers.IntegerField(source="public_id", required=False)

    class Meta:
        model = Roles
        fields = ["name", "publicId"]

    def create(self, data):
        data.update({"public_id": PublicId.create_public_id()})
        return Roles.objects.create(**data)


class ScopeSerializer(serializers.ModelSerializer):
    publicId = serializers.IntegerField(source="public_id", required=False)

    class Meta:
        model = Scopes
        fields = ["name", "publicId"]

    def create(self, data):
        data.update({"public_id": PublicId.create_public_id()})
        return Scopes.objects.create(**data)


class ScopeUpdateSerializer(serializers.Serializer):
    roles = serializers.CharField()
