from django.db import models
from account.models import Account
from store.models import Product, Variation
# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=50)
    done_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    ORDER_STATUS = (
        ('New', 'new'),
        ('Accepted', 'accepted'),
        ('Completed', 'completed'),
        ('Cancelled', 'cancelled')
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    address_1 = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    message = models.CharField(max_length=100)
    total = models.FloatField()
    tax = models.FloatField()
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='New')
    ip_address = models.CharField(blank=True, max_length=30)
    is_ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    order_updated_at = models.DateTimeField(auto_now=True)

    def fullname(self):
        return self.first_name + ' ' + self.last_name

    def main_address(self):
        if self.address_1:
            return self.address_1
        else:
            return self.address_2

    def tax_rate(self):
        rate = (self.tax / self.total) / 100
        return round(rate)     

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ProductOrdered(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    qty = models.IntegerField()
    price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def product_total(self):
        return self.product.discount_price * self.qty

    def __str__(self):
        return self.product.product_name