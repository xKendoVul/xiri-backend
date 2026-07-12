from rest_framework import viewsets

from .models import Business, Menu, Food_Collection
from .serializers import BusinessSerializer, MenuSerializer, FoodCollectionSerializer

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class FoodCollectionViewSet(viewsets.ModelViewSet):
    queryset = Food_Collection.objects.all()
    serializer_class = FoodCollectionSerializer
