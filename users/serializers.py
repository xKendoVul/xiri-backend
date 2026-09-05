from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import User, VerificationRequest

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Este correo ya esta registrado")]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'contact_number', 'country']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            contact_number=validated_data.get('contact_number', ''),
            country=validated_data.get('country', 'Nicaragua'),
            rol='user'
        )
        return user


class VerificationRequestSerializer(serializers.ModelSerializer):
    """
    Serializer para solicitudes de verificación de owners.
    
    - Usuarios normales pueden CREAR solicitudes (POST)
    - Usuarios normales ven SOLO sus propias solicitudes (GET)
    - Admins ven TODAS las solicitudes y pueden cambiar estado
    """
    username = serializers.CharField(source='user.username', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    
    class Meta:
        model = VerificationRequest
        fields = [
            'id', 'user', 'username', 'business_name', 'business_address',
            'id_card_number', 'identity_document', 'state', 'state_display',
            'request_date', 'check_by', 'reviews'
        ]
        read_only_fields = ['user', 'state', 'request_date', 'check_by']

    def create(self, validated_data):
        """El usuario autenticado se asigna automáticamente."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
