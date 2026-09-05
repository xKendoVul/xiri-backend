from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsAdminOrReadOnly
from .models import Department, TraditionalFood, GastronomicRoute, FoodCollection
from .serializers import (
    DepartmentSerializer, TraditionalFoodSerializer, 
    GastronomicRouteSerializer, FoodCollectionSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

class FoodViewSet(viewsets.ModelViewSet):
    queryset = TraditionalFood.objects.all()
    serializer_class = TraditionalFoodSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = TraditionalFood.objects.select_related('department_origin').all()
        dept = self.request.query_params.get('department_origin') or self.request.query_params.get('department')

        if dept:
            queryset = queryset.filter(department_origin_id=dept)

        return queryset

class FoodCollectionViewSet(viewsets.ModelViewSet):
    queryset = FoodCollection.objects.all()
    serializer_class = FoodCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return FoodCollection.objects.select_related('user', 'traditional_food').all()
        return FoodCollection.objects.select_related('user', 'traditional_food').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GastronomicRouteViewSet(viewsets.ModelViewSet):
    queryset = GastronomicRoute.objects.select_related('department').all()
    serializer_class = GastronomicRouteSerializer
    permission_classes = [IsAdminOrReadOnly]