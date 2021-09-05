from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from store.models import Product, Category


def index(request):
    category_id = request.GET.get("category")
    products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
    return render(request, 'index.html', {"products": products,
                                          "categories": Category.objects.all()})
