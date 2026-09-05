from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from .serializers import UserRegisterSerializer, VerificationRequestSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from .models import VerificationRequest
from business.models import Business

class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario registrado con exito"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@perm_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "contact_number": user.contact_number,
        "country": user.country,
        "rol": user.rol,
    })

class VerificationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de verificación de owners.
    
    - Cualquier usuario autenticado puede crear solicitud
    - Usuarios ven solo sus propias solicitudes
    - Admins ven todas las solicitudes y pueden aprobar/rechazar
    """
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'admin':
            return VerificationRequest.objects.select_related('user', 'check_by').all()
        # Usuarios normales ven solo sus solicitudes
        return VerificationRequest.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        if user.rol in ['owner', 'admin'] and not user.is_superuser:
            raise ValidationError({"error": "Ya posees un rol de admin o administrador"})

        if VerificationRequest.objects.filter(user=user, state='pending').exists():
            raise ValidationError({"error": "ya tienes una solicitud de verificacion en revision"})

        serializer.save(user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Aprobar una solicitud de verificación.
        
        Acciones:
        1. Cambia el rol del usuario a 'owner'
        2. Crea el Business asociado
        3. Marca la solicitud como 'approved'
        
        Solo admins pueden ejecutar esta acción.
        """
        # Verificar que es admin
        if not (request.user.is_superuser or request.user.rol == 'admin'):
            return Response(
                {"error": "Solo administradores pueden aprobar solicitudes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        verification_request = self.get_object()
        
        if verification_request.state != 'pending':
            return Response(
                {"error": f"Esta solicitud ya está en estado '{verification_request.state}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # 1. Cambiar rol del usuario a owner
            user = verification_request.user
            user.rol = 'owner'
            user.save()
            
            # 2. Crear el negocio asociado
            Business.objects.create(
                name=verification_request.business_name,
                address=verification_request.business_address,
                owner=user,
                contact_number='',
                latitude=None,
                longitude=None
            )
            
            # 3. Marcar como aprobada
            verification_request.state = 'approved'
            verification_request.check_by = request.user
            verification_request.save()
        
        serializer = VerificationRequestSerializer(verification_request)
        return Response({
            "mensaje": "Solicitud aprobada exitosamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """
        Rechazar una solicitud de verificación.
        
        Acciones:
        1. Marca la solicitud como 'denied'
        2. Guarda el motivo en 'reviews'
        """
        if not (request.user.is_superuser or request.user.rol == 'admin'):
            return Response(
                {"error": "Solo administradores pueden rechazar solicitudes"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        verification_request = self.get_object()
        
        if verification_request.state != 'pending':
            return Response(
                {"error": f"Esta solicitud ya está en estado '{verification_request.state}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = request.data.get('reviews', '')
        
        verification_request.state = 'rejected'
        verification_request.check_by = request.user
        verification_request.reviews = reviews
        verification_request.save()
        
        serializer = VerificationRequestSerializer(verification_request)
        return Response({
            "mensaje": "Solicitud rechazada",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
