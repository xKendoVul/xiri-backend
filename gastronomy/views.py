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

    "Solo la coleccion del usuario en cuestion"
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return Food_Collection.objects.all()
        return Food_Collection.objects.filter(user=user)

    def perform_create(self, serializer):
        "asignacion de usuario autenticado"
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Food.objects.all()
        department_origin = self.request.query_params.get('department_origin')

        if department_origin:
            queryset = queryset.filter(department_origin_id=department_origin)

        return queryset

class GastronomicRouteViewSet(viewsets.ModelViewSet):
    queryset = GastronomicRoute.objects.all()
    serializer_class = GastronomicRouteSerializer
    permission_classes = [IsAdminUserRole]
