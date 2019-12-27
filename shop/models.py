from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, F, FloatField
from django.utils.text import slugify
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
    list_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField()
    featured = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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
    img690x400 = models.ImageField(upload_to="images/")
    img1920x1080 = models.ImageField(upload_to="images/")


class Order(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    items      = models.ManyToManyField('CartItem')
    order_date = models.DateTimeField(auto_now_add=True)
    total      = models.DecimalField(max_digits=6, decimal_places=2)
