import re

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, FloatField
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

ZIP_PATTERN = re.compile("^\d{5}$")

def zip_code_validator(value):
    if not ZIP_PATTERN.match(value):
        raise ValidationError(
            _('%(value)s is not a valid zip code'),
            params={'value': value}
        )

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
    CATEGORIES = (
        (1, 'Food & Drink'),
        (2, 'Clothing'),
        (3, 'Technology'),
        (4, 'Miscellaneous')
    )

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    list_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField()
    featured = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    category = models.IntegerField(default=4, choices=CATEGORIES)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Product ({self.name})'


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


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('product', 'order')


class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    total      = models.DecimalField(max_digits=12, decimal_places=2)
    user       = models.ForeignKey(User, default=None, null=True, related_name="orders", on_delete=models.PROTECT)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    zip = models.CharField(max_length=5, validators=[zip_code_validator])
    country = models.CharField(max_length=255)

    def calc_and_set_total(self):
        total_dict = self.items.aggregate(total=Sum(F('quantity') * F('product__price'),
                                            output_field=FloatField()))
        total = 0.0
        if total_dict.get('total') == None:
            pass
        else:
            total = total_dict['total']

        self.total = total
        self.save()