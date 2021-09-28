import requests
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch import Elasticsearch

from e_shop.settings import LOCAL_HOST
from store.document import ProductDocument
from store.models import Category, Product
from store.serializers import ProductDocumentSerializer


def index(request):
    category_id = request.GET.get("category")
    products = (
        Product.objects.filter(category_id=category_id)
        if category_id
        else Product.objects.all()
    )
    return render(
        request,
        "index.html",
        {"products": products, "categories": Category.objects.all()},
    )


def search(request):
    rest_search_url = LOCAL_HOST + f"/store/search/?search={request.GET.get('search')}"
    response = requests.get(rest_search_url)
    return render(
        request,
        "index.html",
        {"products": response.json(), "categories": Category.objects.all()},
    )


class ProductDocumentView(DocumentViewSet):
    document = ProductDocument
    pagination_class = LimitOffsetPagination
    serializer_class = ProductDocumentSerializer
    fielddata = True
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]
    search_fields = ("name", "description")
    multi_match_search_fields = ("name", "description")
    filter_fields = {
        "name": "name",
        "description": "description",
    }
    ordering_fields = {
        "id": None,
    }
    ordering = ("id",)


# def autocomplete(request):
#     max_items = 5
#     q = request.GET.get('q')
#     if q:
#         sqs = SearchQuerySet().autocomplete(text_auto=q)
#         results = [str(result.object) for result in sqs[:max_items]]
#     else:
#         results = []
#
#     return JsonResponse({
#         'results': results
#     })
