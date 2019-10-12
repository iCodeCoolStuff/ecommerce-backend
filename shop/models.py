from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def create_user(self, email, first_name=None, last_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(email=self.normalize_email(email))
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email, 
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email, 
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user
        

class User(AbstractBaseUser):
    email      = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name  = models.CharField(max_length=255, blank=True, null=True)
    active     = models.BooleanField(default=True)
    staff      = models.BooleanField(default=False)
    admin      = models.BooleanField(default=False)
    timestamp  = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.staff

    @property 
    def is_admin(self):
        return self.admin



class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()