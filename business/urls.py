from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BusinessViewSet, MenuViewSet, FoodCollectionViewSet, RouteBusinessViewSet, BusinessQualificationViewSet, BusinessMenuItemViewSet

router = DefaultRouter()
router.register(r'business', BusinessViewSet)
router.register(r'menu-items', BusinessMenuItemViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'route-business', RouteBusinessViewSet)
router.register(r'qualifications', BusinessQualificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
