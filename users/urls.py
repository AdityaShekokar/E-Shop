from django.urls import path

from users import views

urlpatterns = [
    path("signup/", views.UserView.as_view({"post": "sign_up"})),
    path("login/", views.UserView.as_view({"post": "login"})),
    path("logout/", views.UserLogOutView.as_view({"get": "logout"})),
    path("roles/", views.UserView.as_view({"get": "role_list", "post": "create_role"})),
    path(
        "scopes/", views.UserView.as_view({"get": "scope_list", "post": "create_scope"}),
    ),
    path(
        "scopes/<str:scope_public_id>/", views.UserView.as_view({"patch": "scope_update"}),
    )
]
