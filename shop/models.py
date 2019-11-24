from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, F, FloatField
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem')

    def get_total(self):
        total_dict = self.items.aggregate(total=Sum(F('quantity') * F('product__price'),
                                            output_field=FloatField()))
        if total_dict.get('total') == None:
            return 0.0
        else:
            return total_dict['total']


class ImageSet(models.Model):
    product    = models.OneToOneField(Product, related_name="images", on_delete=models.CASCADE)
    img100x100 = models.ImageField(upload_to="images/")
    img300x400 = models.ImageField(upload_to="images/")
    img500x600 = models.ImageField(upload_to="images/")