from rest_framework import serializers

from gastronomy.models import RouteBusiness
from .models import Business, BusinessQualification, Menu, Food_Collection

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = "__all__"

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"

class FoodCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food_Collection
        fields = "__all__"

class BusinessQualificationSerializer(serializers.ModelSerializer):
    evidence_image = serializers.ImageField(required=True, allow_null=False, allow_empty_file=False)

    class Meta:
        model = BusinessQualification
        fields = ['id', 'business', 'qualification', 'comment', 'evidence_image', 'creation_date']
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
