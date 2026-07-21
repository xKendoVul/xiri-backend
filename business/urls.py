from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, BusinessMenuItemViewSet, MenuViewSet, RouteBusinessViewSet

router = DefaultRouter()
router.register(r'business', BusinessViewSet)
router.register(r'menu-items', BusinessMenuItemViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'route-business', RouteBusinessViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
