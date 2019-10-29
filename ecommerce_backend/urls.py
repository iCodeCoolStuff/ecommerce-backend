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
from django.urls import include, path
from rest_framework import routers

from shop import views

api_router = routers.DefaultRouter()
api_router.register(r'products', views.ProductViewSet)
#api_router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api/v1/', include(api_router.urls)),

    path('api/v1/users/<int:pk>/', views.UserRUDView.as_view(), name="user-detail"),
    path('api/v1/users/', views.UserListCreateView.as_view()),

    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

