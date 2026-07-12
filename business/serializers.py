from rest_framework import serializers
from .models import Business, Menu, Food_Collection

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
