from django.contrib.auth import PermissionDenied
from rest_framework import viewsets
from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from gastronomy.models import RouteBusiness
from users.permissions import IsAdminUserRole, IsOwnerOrAdmin
from .models import Business, BusinessQualification, Menu, Food_Collection
from .serializers import BusinessQualificationSerializer, BusinessSerializer, MenuSerializer, FoodCollectionSerializer

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        if self.request.user.rol not in ['owner','admin'] and not self.request.user.is_superuser:
            raise PermissionDenied("Only users with owner role can register a business")
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return Business.objects.all()

        return Business.objects.filter(owner=user)

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

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

class BusinessQualificationViewSet(viewsets.ModelViewSet):
    queryset = BusinessQualification.objects.all()
    serializer_class = BusinessQualificationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return BusinessQualification.objects.all()

        return BusinessQualification.objects.filter(
            models.Q(user=user) | models.Q(business__owner=user)
        )

class RouteBusinessViewSet(viewsets.ModelViewSet):
    "gestionar los negocios dentro de una ruta"
    queryset = RouteBusiness.objects.all()
    serializer_class = RouteBusinessSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        queryset = RouteBusiness.objects.select_related('route','business').all()
        route_id = self.request.query_params.get('route')
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        return queryset
