from django.db import models
from store.models import Product, Variation
from account.models import Account
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartProduct(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # since many product can have same variation and one product can have many variations
    variation = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    qty = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.discount_price * self.qty

    def __unicode__(self):
        return self.product

