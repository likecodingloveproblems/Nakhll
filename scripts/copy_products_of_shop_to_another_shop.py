from django.db import transaction
from nakhll_market.models import Shop, Product

def run(from_id, to_id, prefix_slug, postfix_slug):
    from_shop = Shop.objects.get(ID=from_id)
    to_shop = Shop.objects.get(ID=to_id)

    products = Product.objects.filter(FK_Shop=from_shop)
    with transaction.atomic():
        for product in products:
                product.pk = None
                product.FK_Shop = to_shop
                product.Slug = prefix_slug + product.Slug[:45] + postfix_slug
                product.Available = True
                product.Publish = True
                product.Inventory = 0
                product.save()
