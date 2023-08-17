from django.db import models
from django.urls import reverse


# Create your models here.


class League(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, unique=True)
    img = models.ImageField(upload_to='images/league')

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, unique=True)
    img = models.ImageField(upload_to='images/club')
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return self.name