import requests
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import transaction, IntegrityError
from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope, \
    TokenMatchesOASRequirements
from oauth2_provider.models import Application, AccessToken
from rest_framework import viewsets
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import RegistrationSerializer, LoginSerializer
from e_shop.settings import LOCAL_HOST


class UserView(viewsets.ViewSet):

    def sign_up(self, req):
        serialize_data = RegistrationSerializer(data=req.data)
        if serialize_data.is_valid(raise_exception=True):
            with transaction.atomic():
                user = serialize_data.save()
                Application.objects.create(user=user, authorization_grant_type="password",
                                           client_type="Confidential", name=user.email)
            return Response({"Message": f"User {user.username} created successfully."})

    def login(self, req):
        serialize_data = LoginSerializer(data=req.data)
        if serialize_data.is_valid(raise_exception=True):
            with transaction.atomic():
                email = serialize_data.data.get("email")
                password = serialize_data.data.get("passWord")
                try:
                    account = User.objects.get(email=email)
                except User.DoesNotExist as e:
                    raise ValidationError({"Error": f"User {email} does not exist."})
                if not check_password(password, account.password):
                    raise ValidationError({"Error": "Incorrect Login credentials"})
                application = Application.objects.get(user=account)
                body_param = {"username": account.username,
                              "password": password,
                              "client_id": application.client_id,
                              "client_secret": application.client_secret,
                              "grant_type": "password"}
                response = requests.post(LOCAL_HOST + "/o/token/", data=body_param)
                if response.status_code != 200:
                    raise APIException(response.json(), status_code=response.status_code)
                return Response(response.json())


class UserLogOutView(viewsets.ViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "POST": [["create"]],
        "GET": [["read"]]
    }

    def logout(self, req):
        token = req.auth.token
        application = Application.objects.get(user=req.user)
        data = {
            "token": token,
            "client_id": application.client_id,
            "client_secret": application.client_secret,
        }
        requests.post(LOCAL_HOST + "/o/revoke_token/", data=data)
        return Response({"message": 'User Logged out successfully'})
