import urllib.parse

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramDistance

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
        serializer = ProductSerializer(q, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def new(self, request, pk=None):
        q = self.queryset.filter(new=True)
        serializer = ProductSerializer(q, many=True, context={'request': request})
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


class SearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query_param = self.request.GET.get('q', '')
        category_param = self.request.GET.get('category', '')

        query = urllib.parse.unquote_plus(query_param)
        category = urllib.parse.unquote_plus(category_param)

        if query == '':
            return Product.objects.all()

        try:
            category = int(category)
        except:
            pass

        valid_categories = map(lambda x: x[0], Product.CATEGORIES)

        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')

        queryset = Product.objects.annotate(rank=(SearchRank(vector, SearchQuery(query)))).filter(rank__gte=0.2).order_by('-rank')

        return queryset.filter(category=category) if category in valid_categories else queryset