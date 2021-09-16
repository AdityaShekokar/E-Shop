from django.urls import path

from users import views

urlpatterns = [
    path("signup/", views.UserView.as_view({"post": "sign_up"})),
    path("login/", views.UserView.as_view({"post": "login"})),
    path("logout/", views.UserLogOutView.as_view({"get": "logout"})),
]