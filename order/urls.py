from django.urls import path
from .views import OrderViewSet, CartViewSet

urlpatterns = [

]

from rest_framework import routers

router = routers.DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('cart', CartViewSet, basename='cart')

urlpatterns += router.urls
