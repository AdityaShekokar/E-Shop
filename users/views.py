import requests
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError, transaction
from django.shortcuts import render

# Create your views here.
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
    TokenHasReadWriteScope,
    TokenMatchesOASRequirements,
)
from oauth2_provider.models import AccessToken, Application
from rest_framework import viewsets
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from e_shop.common import CustomPermissions, validate_url_value
from e_shop.settings import LOCAL_HOST
from users.models import Roles, Scopes, User
from users.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    RoleSerializer,
    ScopeSerializer,
    ScopeUpdateSerializer,
)


class UserView(viewsets.ViewSet):
    def sign_up(self, req):
        serialize_data = RegistrationSerializer(data=req.data)
        if serialize_data.is_valid(raise_exception=True):
            with transaction.atomic():
                user = serialize_data.save()
                Application.objects.create(
                    user=user,
                    authorization_grant_type="password",
                    client_type="Confidential",
                    name=user.email,
                )
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
                body_param = {
                    "username": account.username,
                    "password": password,
                    "client_id": application.client_id,
                    "client_secret": application.client_secret,
                    "grant_type": "password",
                }
                response = requests.post(LOCAL_HOST + "/o/token/", data=body_param)
                if response.status_code != 200:
                    raise APIException(response.json())
                return Response(response.json())

    def create_role(self, req):
        serialize_data = RoleSerializer(data=req.data)
        if serialize_data.is_valid(raise_exception=True):
            serialize_data.save()
            return Response(
                {
                    "message": f"successfully create {serialize_data.data.get('name')} role."
                }
            )

    def role_list(self, _):
        roles = Roles.objects.all()
        serializer_data = RoleSerializer(roles, many=True)
        return Response(serializer_data.data)

    def create_scope(self, req):
        serialize_data = ScopeSerializer(data=req.data)
        if serialize_data.is_valid(raise_exception=True):
            serialize_data.save()
            return Response(
                {
                    "message": f"successfully create {serialize_data.data.get('name')} scope."
                }
            )

    def scope_update(self, req, scope_public_id):
        try:
            validate_url_value(scope_public_id, "scopeId")
            serialize_data = ScopeUpdateSerializer(data=req.data)
            if serialize_data.is_valid(raise_exception=True):
                scope = Scopes.objects.get(public_id=scope_public_id)
                for role in serialize_data.data.get("roles").split(","):
                    query_filter = role.strip()
                    role = Roles.objects.get(name__icontains=query_filter)
                    scope.roles.add(role)
                scope.save()
                return Response({"message": "Scope updated successfully"})
        except Scopes.DoesNotExist:
            raise NotFound({"error": f"No scope found on public id {scope_public_id}"})
        except Roles.DoesNotExist:
            raise NotFound({"error": f"Role '{query_filter}' does not exist."})

    def scope_list(self, _):
        scopes = Scopes.objects.all()
        serializer_data = ScopeSerializer(scopes, many=True)
        return Response(serializer_data.data)


class UserLogOutView(viewsets.ViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenMatchesOASRequirements, CustomPermissions]
    required_alternate_scopes = {
        "POST": [["create"]],
        "GET": [["create"], ["custom_scope1", "custom_scope2"]],
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
        return Response({"message": "User Logged out successfully"})
