from rest_framework import serializers

from .models import Business, BusinessQualification, Menu, RouteBusiness, BusinessMenuItem

class BusinessSerializer(serializers.ModelSerializer):
    """Serializer para negocios."""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'contact_number', 'latitude', 'longitude',
                  'owner', 'owner_name', 'created_at']
        read_only_fields = ['owner', 'created_at']

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
    traditional_food_name = serializers.CharField(source='traditional_food.name', read_only=True)
    
    class Meta:
        model = BusinessMenuItem
        fields = ['id', 'name', 'description', 'image', 'business', 'business_name',
                  'traditional_food', 'traditional_food_name', 'is_traditional_variant', 
                  'counts_for_album', 'created_at']
        read_only_fields = ['created_at']


class MenuSerializer(serializers.ModelSerializer):
    """Serializer para el precio de un item en el menú."""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    
    class Meta:
        model = Menu
        fields = ['id', 'business', 'business_name', 'menu_item', 'menu_item_name', 'price']

class FoodCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food_Collection
        fields = "__all__"
        read_only_fields = ['user']  ##permiso de nuevo


class BusinessQualificationSerializer(serializers.ModelSerializer):
    evidence_image = serializers.ImageField(required=True, allow_null=False, allow_empty_file=False)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = BusinessQualification
        fields = ['id', 'user', 'username', 'business', 'qualification', 'comment', 'evidence_image', 'creation_date']
        read_only_fields = ['user', 'creation_date']

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
