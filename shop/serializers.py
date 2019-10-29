from django.contrib.auth.hashers import check_password

from rest_framework import serializers
from .models import User, Product


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
            raise serializers.ValidationError('Passwords do not match.')      


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
        user = User()
        user.first_name = validated_data['first_name']
        user.last_name  = validated_data['last_name']
        user.email      = validated_data['email']
        if validated_data['password'] == validated_data['password_confirmation']:
            user.set_password(validated_data['password'])
            user.save()
            return user
        else:
            raise ValidationError('Password and confirmation do not match.')