from rest_framework import generics, viewsets

from .models import User, Product
from .serializers import ProductSerializer, UserRUDSerializer, UserRegistrationSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRUDSerializer


class UserListCreateView(generics.ListCreateAPIView):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = UserRUDSerializer

    def get_queryset(self):
        return User.objects.all()
    