import urllib.parse

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramDistance

from rest_framework import generics, viewsets, status

from rest_framework.decorators import action, api_view
from rest_framework.response   import Response

from rest_framework_simplejwt.views import TokenObtainPairView

from .models      import User, Product, Cart, CartItem, Order, OrderItem

from .permissions import IsAdminOrWriteOnly, UserPermission
from .serializers import (
    ProductSerializer, 
    UserRUDSerializer, 
    UserListCreateSerializer, 
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    CustomTokenObtainPairSerializer
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
    queryset = Order.objects.all()
    permission_classes = [IsAdminOrWriteOnly]


class AuthOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [UserPermission]

    def get_queryset(self):
        user = User.objects.get(pk=self.kwargs['user_pk'])
        return Order.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs['user_pk']
        return context


'''class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()'''


class SearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query_param = self.request.GET.get('q', '')
        category_param = self.request.GET.get('category', '')

        query = urllib.parse.unquote_plus(query_param)
        category = urllib.parse.unquote_plus(category_param)

        try:
            category = int(category)
        except:
            pass

        queryset = None
        if query == '':
            queryset = Product.objects.all()
        else:
            vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
            queryset = Product.objects.annotate(rank=(SearchRank(vector, SearchQuery(query)))).filter(rank__gte=0.2).order_by('-rank')

        valid_categories = map(lambda x: x[0], Product.CATEGORIES)

        return queryset.filter(category=category) if category in valid_categories else queryset


@api_view(['GET'])
def recommendations(request):
    if request.method != 'GET':
        return Response({'error': 'Only \'GET\' is allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    pk = request.query_params.get('id', '')
    if pk == '':
        return Response({'error': 'Missing query param \'id\''}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pk = int(pk)
    except:
        return Response({'error': '\'id\' is not an integer'}, status=status.HTTP_400_BAD_REQUEST)

    if not Product.objects.all().filter(pk=pk):
        return Response({'error': 'Can\'t generate recommendations from a product that does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    
    obj = Product.objects.get(pk=pk)

    queryset = Product.objects.all().filter(category=obj.category).exclude(pk=pk).order_by('?')[:4]

    serializer = ProductSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

 
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer