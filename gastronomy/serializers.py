from rest_framework import serializers
from .models import Department, TraditionalFood, GastronomicRoute, FoodCollection

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class TraditionalFoodSerializer(serializers.ModelSerializer):
    """Serializer para platillos tradicionales del álbum."""
    department_name = serializers.CharField(source='department_origin.name', read_only=True)
    
    class Meta:
        model = TraditionalFood
        fields = ['id', 'name', 'description', 'image', 'cultural_origin', 
                  'department_origin', 'department_name', 'created_at']


class FoodCollectionSerializer(serializers.ModelSerializer):
    """Serializer para la colección de platillos del usuario."""
    food_name = serializers.CharField(source='traditional_food.name', read_only=True)
    department_name = serializers.CharField(source='traditional_food.department_origin.name', read_only=True)
    food_image = serializers.ImageField(source='traditional_food.image', read_only=True)
    
    class Meta:
        model = FoodCollection
        fields = ['id', 'user', 'traditional_food', 'food_name', 'department_name', 
                  'food_image', 'complete', 'registered_date']
        read_only_fields = ['user', 'registered_date']


class GastronomicRouteSerializer(serializers.ModelSerializer):
    """Serializer para rutas gastronómicas."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = GastronomicRoute
        fields = ['id', 'name', 'description', 'department', 'department_name']
