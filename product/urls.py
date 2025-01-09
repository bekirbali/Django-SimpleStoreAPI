from django.urls import path
from .views import ProductViewSet

urlpatterns = [

]

from rest_framework import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet)


urlpatterns += router.urls
