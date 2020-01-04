from django.contrib.auth.hashers import check_password

from rest_framework import serializers

from . import exceptions
from . import models
from .models import (
    User,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem
)


class ImageSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImageSet
        fields = ['img100x100', 'img690x400', 'img1920x1080']


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    images = ImageSetSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('pk', 'name', 'price', 'list_price', 'description', 'on_sale', 
                    'new', 'featured', 'category', 'images', 'url', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'slug': {'read_only': True},
            'url': {'lookup_field': 'slug'}
        }


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


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['pk', 'product_id', 'product', 'quantity']
    
    def create(self, validated_data):
        product_id = validated_data['product_id']
        quantity = validated_data['quantity']
        order = validated_data['order']

        product = Product.objects.get(pk=product_id)
        orderItem = OrderItem.objects.create(product=product, quantity=quantity)
        return orderItem


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['pk', 'first_name', 'last_name', 'address1', 'address2', 'city', 'region', 
                    'zip', 'country', 'items', 'total', 'order_date']
        read_only_fields = ['total', 'order_date']

    def create(self, validated_data):
        items = validated_data['items']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        address1 = validated_data['address1']
        address2 = validated_data['address2']
        city = validated_data['city']
        region = validated_data['region']
        zip = validated_data['zip']
        country = validated_data['country']

        productIds = []
        for item in items:
            product = None
            try:
                id = item['product_id']
                product = Product.objects.get(pk=id)
            except:
                raise exceptions.ItemDoesntExist(f'Product with a product id of {id} does not exist')

            if product.pk in productIds:
                raise exceptions.ItemAlreadyExists(f'Duplicate items with a product id of {product.pk}')
            productIds.append(product.pk)

        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            address1=address1,
            address2=address2,
            city=city,
            region=region,
            zip=zip,
            country=country,
            total=0.0
        )

        orderItems = []
        for item in items:
            orderItem = OrderItem.objects.create(
                product=Product.objects.get(pk=item['product_id']),
                quantity=item['quantity'],
                order=order
            )
            orderItems.append(orderItem)

        order.items.set(orderItems)
        order.calc_and_set_total()
        return order