from rest_framework import generics, viewsets

from .models      import User, Product, Cart, CartItem, Order
from .permissions import IsAdminOrWriteOnly, UserPermission
from .serializers import (
    ProductSerializer, 
    UserRUDSerializer, 
    UserListCreateSerializer, 
    CartSerializer,
    CartItemSerializer,
    OrderCreateSerializer,
    OrderModelSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UserListCreateView(generics.ListCreateAPIView):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserListCreateSerializer
    #permission_classes = [IsAdminOrWriteOnly]


class UserRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserRUDSerializer
    #permission_classes = [UserPermission]


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user_id=self.kwargs['pk'])


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        cart = User.objects.get(pk=self.kwargs['user_pk']).cart
        return CartItem.objects.filter(cart=cart)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs['user_pk']
        return context


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderModelSerializer

    def get_queryset(self):
        user = User.objects.get(pk=self.kwargs['user_pk'])
        return Order.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs['user_pk']
        return context


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs['user_pk']
        return context