from django.urls import path

from store import views

urlpatterns = [
    path("", views.index),
    path("filter/", views.search, name="filter_view"),
    path("search/", views.ProductDocumentView.as_view({"get": "list"})),
]
