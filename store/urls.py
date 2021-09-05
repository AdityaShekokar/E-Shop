from django.urls import path

from store import views

urlpatterns = [
    path("index/", views.index)
]
