from django.contrib.auth import PermissionDenied
from rest_framework import viewsets
from django.db import models
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from users.permissions import IsAdminUserRole, IsOwnerOrAdmin
from .models import Business, BusinessQualification, Menu, RouteBusiness, BusinessMenuItem
from .serializers import (
    BusinessQualificationSerializer, BusinessSerializer, 
    BusinessMenuItemSerializer, MenuSerializer, 
    RouteBusinessSerializer
)


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        if self.request.user.rol not in ['owner','admin'] and not self.request.user.is_superuser:
            raise PermissionDenied("Solo usuarios con rol owner pueden registrar negocios")
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return Business.objects.all()
        return Business.objects.filter(owner=user)

    @action(detail=True, methods=['patch'], permission_classes=[IsOwnerOrAdmin])
    def complete_profile(self, request, pk=None):
        """
        Endpoint para que el owner complete la información de su negocio.
        
        Campos editables:
        - contact_number
        - latitude
        - longitude
        
        Solo el owner del negocio o admin pueden ejecutar esta acción.
        """
        business = self.get_object()
        
        # Verificar ownership
        if business.owner != request.user and request.user.rol != 'admin' and not request.user.is_superuser:
            return Response(
                {"error": "Solo puedes editar tu propio negocio"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Campos permitidos para actualizar
        allowed_fields = ['contact_number', 'latitude', 'longitude']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(business, field, request.data[field])
        
        business.save()
        
        serializer = BusinessSerializer(business)
        return Response({
            "mensaje": "Perfil del negocio completado",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class BusinessMenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet para platillos del menú de un negocio."""
    queryset = BusinessMenuItem.objects.all()
    serializer_class = BusinessMenuItemSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business and business.owner != self.request.user:
            if self.request.user.rol != 'admin' and not self.request.user.is_superuser:
                raise PermissionDenied("Solo puedes agregar platillos a tus propios negocios")
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        queryset = BusinessMenuItem.objects.select_related('business', 'traditional_food').all()

        business_id = self.request.query_params.get('business')
        if business_id:
            queryset = queryset.filter(business_id=business_id)
            return queryset

        if user.is_superuser or user.rol == 'admin':
            return queryset
        return queryset.filter(business__owner=user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUserRole])
    def validate_for_album(self, request, pk=None):
        """
        Endpoint para que admin marque un item del menú como válido para completar el álbum.
        
        Acciones:
        - Marca is_traditional_variant = True
        - Asocia un traditional_food si se proporciona
        
        Solo admins pueden ejecutar esta acción.
        """
        if not (request.user.is_superuser or request.user.rol == 'admin'):
            return Response(
                {"error": "Solo administradores pueden validar items para el álbum"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        menu_item = self.get_object()
        
        # Marcar como variante tradicional
        menu_item.is_traditional_variant = True
        
        # Si se proporciona un traditional_food, asociarlo
        traditional_food_id = request.data.get('traditional_food')
        if traditional_food_id:
            menu_item.traditional_food_id = traditional_food_id
        
        menu_item.save()
        
        serializer = BusinessMenuItemSerializer(menu_item)
        return Response({
            "mensaje": "Item validado para el álbum",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class MenuViewSet(viewsets.ModelViewSet):
    """ViewSet para precios del menú."""
    queryset = Menu.objects.select_related('business', 'menu_item').all()
    serializer_class = MenuSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business and business.owner != self.request.user:
            if self.request.user.rol != 'admin' and not self.request.user.is_superuser:
                raise PermissionDenied("Solo puedes agregar precios a tus propios negocios")
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        queryset = Menu.objects.select_related('business', 'menu_item').all()

        business_id = self.request.query_params.get('business')
        if business_id:
            queryset = queryset.filter(business_id=business_id)
            return queryset

        if user.is_superuser or user.rol == 'admin':
            return queryset
        return queryset.filter(business__owner=user)


class BusinessQualificationViewSet(viewsets.ModelViewSet):
    queryset = BusinessQualification.objects.all()
    serializer_class = BusinessQualificationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        business_id = self.request.query_params.get('business')

        if business_id:
            return BusinessQualification.objects.filter(business_id=business_id)

        if user.is_superuser or user.rol == 'admin':
            return BusinessQualification.objects.select_related('user', 'business').all()
        return BusinessQualification.objects.select_related('user', 'business').filter(
            models.Q(user=user) | models.Q(business__owner=user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteBusinessViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar los negocios dentro de una ruta."""
    queryset = RouteBusiness.objects.select_related('route', 'business').all()
    serializer_class = RouteBusinessSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        queryset = RouteBusiness.objects.select_related('route', 'business').all()
        route_id = self.request.query_params.get('route')
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        return queryset
