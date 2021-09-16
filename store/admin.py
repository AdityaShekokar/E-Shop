from django.contrib import admin

# Register your models here.
from store.models import Category, Product


class AdminProduct(admin.ModelAdmin):
    list_display = ["name", "price", "description", "category"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(Product, AdminProduct)
admin.site.register(Category, CategoryAdmin)
