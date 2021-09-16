from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from store.document import ProductDocument
from store.models import Product


class ProductDocumentSerializer(DocumentSerializer):
    class Meta(object):
        model = Product
        document = ProductDocument
        fields = ("name", "description", "price", "image")

        def get_location(self, obj):
            """Represent location value."""
            try:
                return obj.location.to_dict()
            except:
                return {}
