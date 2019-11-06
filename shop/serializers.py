from django.contrib.auth.hashers import check_password

from rest_framework import serializers

from . import exceptions
from .models import User, Product, Cart, CartItem


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('pk', 'url', 'name', 'price', 'description')


class UserRUDSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ('pk', 'url', 'first_name', 'last_name', 'email', 'password')
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


class UserListCreateSerializer(serializers.HyperlinkedModelSerializer):  
    password_confirmation = serializers.CharField(allow_blank=False, write_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ('pk', 'url', 'first_name', 'last_name', 'email', 'password', 'password_confirmation')
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
        cart       = User.objects.get(pk=self.context['user_id']).cart

        cart_item = CartItem.objects.create(
            quantity=quantity,
            product=product,
            cart=cart
        )

        cart_item.save()
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['items']