from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsAdminUserRole
from .models import Department, TraditionalFood, GastronomicRoute, Food_Collection
from .serializers import (
    DepartmentSerializer, TraditionalFoodSerializer, 
    GastronomicRouteSerializer, FoodCollectionSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUserRole]

class FoodViewSet(viewsets.ModelViewSet):
    queryset = TraditionalFood.objects.all()
    serializer_class = TraditionalFoodSerializer
    permission_classes = [IsAdminUserRole]

class FoodCollectionViewSet(viewsets.ModelViewSet):
    queryset = Food_Collection.objects.all()
    serializer_class = FoodCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return Food_Collection.objects.select_related('user', 'traditional_food').all()
        return Food_Collection.objects.select_related('user', 'traditional_food').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GastronomicRouteViewSet(viewsets.ModelViewSet):
    queryset = GastronomicRoute.objects.all()
    serializer_class = GastronomicRouteSerializer
    permission_classes = [IsAdminUserRole]
