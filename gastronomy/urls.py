from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, FoodViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'foods', FoodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
