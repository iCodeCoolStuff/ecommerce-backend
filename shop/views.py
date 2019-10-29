from rest_framework import generics, viewsets

from .models import User, Product
from .serializers import ProductSerializer, UserRUDSerializer, UserListCreateSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UserListCreateView(generics.ListCreateAPIView):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserListCreateSerializer


class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserRUDSerializer 
    