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


##permiso Hadyi, tambien ocupaba editar aqui para poder filtrar correctamente las comidas por departamento en el Expo
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
