from django.contrib.auth.hashers import check_password

from rest_framework import serializers

from . import exceptions
from . import models
from .models import (
    User,
    Product,
    Cart,
    CartItem,
    Order
)


class ImageSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImageSet
        fields = ['img100x100', 'img300x400', 'img500x600']


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSetSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('pk', 'name', 'price', 'description', 'new', 'featured', 'images')


class UserRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        """
        Updates user instance and checks if passwords match. 
        
        If passwords match, the object is saved. If not, then a ValidationError is raised.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name  = validated_data.get('last_name',  instance.last_name)
        instance.email      = validated_data.get('email',      instance.email)

        if check_password(validated_data['password'], instance.password):
            instance.save()
            return instance
        else:
            raise exceptions.PasswordMismatchException()      


class UserListCreateSerializer(serializers.ModelSerializer):  
    password_confirmation = serializers.CharField(allow_blank=False, write_only=True)

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'password', 'password_confirmation')
        extra_kwargs = {
            'password': {'write_only': True},
            'url'     : {'read_only' : True},
            'pk'      : {'read_only' : True}
        }
    
    def create(self, validated_data):
        """
        Creates a new user with a first name, last name, email, and password
        """
        first_name = validated_data['first_name']
        last_name  = validated_data['last_name']
        email      = validated_data['email']
        password   = validated_data['password']
        
        if password == validated_data['password_confirmation']:
            user = User.objects.create_user(first_name=first_name,
                                            last_name=last_name,
                                            email=email,
                                            password=password)
            return user
        else:
            raise exceptions.PasswordConfirmationMismatchException()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['pk', 'product', 'product_id', 'quantity']
        extra_kwargs = {
            'item_id': {'write_only': True}
        }

    def create(self, validated_data):
        quantity   = validated_data['quantity']
        product_id = validated_data['product_id']
        product    = Product.objects.get(pk=product_id)
        cart       = Cart.objects.get(user_id=self.context['user_id'])

        cart_item = CartItem.objects.create(quantity=quantity, product=product)
        cart_item.cart_set.add(cart)
        cart_item.save()
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'items', 'total']

    def get_total(self, obj):
        return obj.get_total()


class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['pk', 'user', 'total', 'order_date', 'items']
        read_only_fields = fields

    def create(self, validated_data):
        user  = User.objects.get(pk=self.context['user_id'])
        cart  = Cart.objects.get(user=user)

        if not cart.items.exists():
            raise exceptions.EmptyCartException()

        order = Order(user=user, total=cart.get_total())
        order.save()
        order.items.set(cart.items.all())

        cart.items.clear()
        return order