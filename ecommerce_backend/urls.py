"""ecommerce_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shop import views

api_router = routers.DefaultRouter()
api_router.register(r'products', views.ProductViewSet)
api_router.register(r'orders', views.OrderViewSet)

item_list = views.CartItemViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

item_detail = views.CartItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

order_create = views.OrderViewSet.as_view({
    'post': 'create'
})

order_list = views.OrderViewSet.as_view({
    'get': 'list'
})

auth_order_view = views.AuthOrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

order_detail = views.AuthOrderViewSet.as_view({
    'get': 'retrieve',
    #'put': 'update',
    #'patch': 'partial_update',
    'delete': 'destroy'
})
 

urlpatterns = [
    path('v1/', include(api_router.urls)),
    path('v1/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('v1/users/', views.UserListCreateView.as_view()),
    #path('v1/users/<int:pk>/', views.UserRUDView.as_view(), name="user-detail"),

    #path('v1/users/<int:pk>/cart/', views.CartView.as_view(), name="cart-detail"),
    #path('v1/users/<int:user_pk>/cart/checkout', order_create, name="order-create"),
    #path('v1/users/<int:user_pk>/cart/items/', item_list, name="item-list"),
    #path('v1/users/<int:user_pk>/cart/items/<int:pk>/', item_detail, name="item-detail"),

    path('v1/users/<int:user_pk>/orders/', auth_order_view, name="order-list"),
    path('v1/users/<int:user_pk>/orders/<int:pk>/', order_detail, name="order-detail"),

    path('v1/search/', views.SearchView.as_view(), name="search-list"),
    path('v1/recommendations', views.recommendations),

    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)