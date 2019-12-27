from rest_framework import generics, viewsets

from rest_framework.decorators import action
from rest_framework.response   import Response

from .models      import User, Product, Cart, CartItem, Order

from .permissions import IsAdminOrWriteOnly, UserPermission
from .serializers import (
    ProductSerializer, 
    UserRUDSerializer, 
    UserListCreateSerializer, 
    CartSerializer,
    CartItemSerializer,
    OrderSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    @action(methods=['GET'], detail=False)
    def featured(self, request, pk=None):
        q = self.queryset.filter(featured=True)
        serializer = ProductSerializer(q, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def new(self, request, pk=None):
        q = self.queryset.filter(new=True)
        serializer = ProductSerializer(q, many=True)
        return Response(serializer.data)


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
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = User.objects.get(pk=self.kwargs['user_pk'])
        return Order.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs['user_pk']
        return context
