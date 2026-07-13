from rest_framework import viewsets

from users.permissions import IsAdminUserRole
from .models import Department, Food, GastronomicRoute
from .serializers import DepartmentSerializer, FoodSerializer, GastronomicRouteSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUserRole]

class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAdminUserRole]

class GastronomicRouteViewSet(viewsets.ModelViewSet):
    queryset = GastronomicRoute.objects.all()
    serializer_class = GastronomicRouteSerializer
    permission_classes = [IsAdminUserRole]
