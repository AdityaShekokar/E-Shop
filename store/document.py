from django_elasticsearch_dsl import Document, Index, fields

from .models import Product

PUBLISHER_INDEX = Index("eshop_elastic")

PUBLISHER_INDEX.settings(number_of_shards=1, number_of_replicas=1)


@PUBLISHER_INDEX.doc_type
class ProductDocument(Document):
    id = fields.IntegerField(attr="id")
    fielddata = True

    class Django:
        model = Product
        fields = ["name", "description", "price", "image"]
