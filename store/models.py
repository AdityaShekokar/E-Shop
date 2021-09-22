from django.db import models

# Create your models here.
from e_shop.common import CreateUpdateDate, SafeDeleteModel, UniqueIds


class Product(CreateUpdateDate, UniqueIds, SafeDeleteModel):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=200, default="")
    image = models.ImageField(upload_to="uploads/products/")
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"


class Category(CreateUpdateDate, UniqueIds, SafeDeleteModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"
