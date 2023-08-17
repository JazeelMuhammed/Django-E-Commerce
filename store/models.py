from django.db import models
from category.models import Club
from django.db.models import Avg, Count
from django.urls import reverse
from account.models import Account


# Create your models here.


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    actual_price = models.IntegerField()
    discount_price = models.IntegerField()
    stock = models.IntegerField()
    product_img = models.ImageField(upload_to='images/home')
    product_img2 = models.ImageField(upload_to='images/home', blank=True)
    is_available = models.BooleanField(default=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=50, default='', blank=True)

    def discount_rate(self):
        dis = int((self.actual_price - self.discount_price)/self.actual_price * 100)
        return round(dis)

    def get_url(self):
        return reverse('product_details', args=[self.id],)

    def average_rating(self):
        reviews = ProductReview.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def total_reviews(self):
        reviews = ProductReview.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    images = models.ImageField(upload_to='images/product')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class VariationManager(models.Manager):
    def size(self):
        return super(VariationManager, self).filter(size='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.size


class RetroCategory(models.Model):
    period = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)


class RetroProduct(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(max_length=250, blank=True)
    actual_price = models.IntegerField()
    discount_price = models.IntegerField()
    stock = models.IntegerField()
    product_img = models.ImageField(upload_to='images/home')
    is_available = models.BooleanField(default=True)
    team = models.ForeignKey(Club, on_delete=models.CASCADE)
    category = models.ForeignKey(RetroCategory, on_delete=models.CASCADE)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=400, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class UserWishList(models.Model):
    wishlist_id = models.CharField(max_length=200, blank=True)
    date_added = models.DateField(auto_now_add=True)


class WishListProduct(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # since many product can have same variation and one product can have many variations
    variation = models.ManyToManyField(Variation, blank=True)
    user_wishlist = models.ForeignKey(UserWishList, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)

