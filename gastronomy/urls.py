from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, FoodViewSet, FoodCollectionViewSet, GastronomicRouteViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'foods', FoodViewSet)
router.register(r'collections', FoodCollectionViewSet)
router.register(r'routes', GastronomicRouteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
