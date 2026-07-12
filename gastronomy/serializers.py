from rest_framework import serializers
from .models import Department, Food

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model: Food
        fields = "__all__"
