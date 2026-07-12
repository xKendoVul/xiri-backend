from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, MenuViewSet, FoodCollectionViewSet

router = DefaultRouter()
router.register(r'business', BusinessViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'foods', FoodCollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
