from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from store.models import Product


def index(request):
    return render(request, 'index.html', {"products": Product.objects.all()})
