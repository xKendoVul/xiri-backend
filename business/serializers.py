from rest_framework import serializers
from django.db import transaction

from .models import Business, BusinessQualification, Menu, RouteBusiness, BusinessMenuItem

class BusinessSerializer(serializers.ModelSerializer):
    """Serializer para negocios."""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    average_rating = serializers.FloatField(read_only=True, default=0.0)
    total_reviews = serializers.IntegerField(read_only=True, default=0)
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'contact_number', 'latitude', 'longitude',
                  'owner', 'owner_name', 'average_rating', 'total_reviews', 'created_at']
        read_only_fields = ['owner', 'created_at', 'average_rating', 'total_reviews']

    def update(self, instance, validated_data):
        """Permitir actualización parcial de campos."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BusinessMenuItemSerializer(serializers.ModelSerializer):
    """Serializer para platillos del menú de un negocio."""
    counts_for_album = serializers.BooleanField(read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_address = serializers.CharField(source='business.address', read_only=True)
    traditional_food_name = serializers.CharField(source='traditional_food.name', read_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        business = attrs.get('business', getattr(self.instance, 'business', None))
        if business and business.owner_id != user.pk and not (user.is_superuser or user.rol == 'admin'):
            raise serializers.ValidationError({'business': 'Solo puedes usar tus propios negocios'})
        if 'is_traditional_variant' in attrs and not (user.is_superuser or user.rol == 'admin'):
            current = self.instance.is_traditional_variant if self.instance else False
            if attrs['is_traditional_variant'] != current:
                raise serializers.ValidationError({'is_traditional_variant': 'Solo administradores pueden validar variantes'})
        return attrs

    class Meta:
        model = BusinessMenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'business', 'business_name',
                  'business_address', 'traditional_food', 'traditional_food_name',
                  'is_traditional_variant', 'counts_for_album', 'created_at']
        read_only_fields = ['created_at']


class MenuSerializer(serializers.ModelSerializer):
    """Serializer para el precio de un item en el menú."""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        business = attrs.get('business', getattr(self.instance, 'business', None))
        item = attrs.get('menu_item', getattr(self.instance, 'menu_item', None))
        if business and business.owner_id != user.pk and not (user.is_superuser or user.rol == 'admin'):
            raise serializers.ValidationError({'business': 'Solo puedes usar tus propios negocios'})
        if item and business and item.business_id != business.pk:
            raise serializers.ValidationError({'menu_item': 'El platillo no pertenece a este negocio'})
        if attrs.get('price', 0) < 0:
            raise serializers.ValidationError({'price': 'El precio no puede ser negativo'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        menu = super().create(validated_data)
        BusinessMenuItem.objects.filter(pk=menu.menu_item_id).update(price=menu.price)
        return menu

    @transaction.atomic
    def update(self, instance, validated_data):
        menu = super().update(instance, validated_data)
        BusinessMenuItem.objects.filter(pk=menu.menu_item_id).update(price=menu.price)
        return menu

    class Meta:
        model = Menu
        fields = ['id', 'business', 'business_name', 'menu_item', 'menu_item_name', 'price']


class BusinessQualificationSerializer(serializers.ModelSerializer):
    evidence_image = serializers.ImageField(required=True, allow_null=False, allow_empty_file=False)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = BusinessQualification
        fields = ['id', 'user', 'username', 'business', 'qualification', 'comment', 'evidence_image', 'creation_date']
        read_only_fields = ['user', 'creation_date']

    def validate(self, attrs):
        user = self.context['request'].user if self.instance is None else self.instance.user
        business = attrs.get('business', getattr(self.instance, 'business', None))
        existing = BusinessQualification.objects.filter(user=user, business=business)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError({'business': 'Ya calificaste este negocio'})
        return attrs

    def validate_qualification(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RouteBusinessSerializer(serializers.ModelSerializer):
    route_name = serializers.CharField(source='route.name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_address = serializers.CharField(source='business.address', read_only=True)

    class Meta:
        model = RouteBusiness
        fields = ['id', 'route', 'route_name', 'business', 'business_name',
                  'business_address', 'suggested_order']
