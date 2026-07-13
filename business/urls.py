from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, MenuViewSet, FoodCollectionViewSet, RouteBusinessViewSet

router = DefaultRouter()
router.register(r'business', BusinessViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'collections', FoodCollectionViewSet)
router.register(r'route-business', RouteBusinessViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
