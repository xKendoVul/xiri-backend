from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, FoodViewSet, GastronomicRouteViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'foods', FoodViewSet)
router.register(r'routes', GastronomicRouteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
