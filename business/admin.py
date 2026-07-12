from django.contrib import admin
from .models import Business, Menu, Food_Collection

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'latitude', 'longitude', 'contact_number')
    search_fields = ('name', 'address')
    list_filter = ('owner',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('business', 'food', 'price')
    list_filter = ('business', 'food')
    # Buscador rápido por el nombre del negocio o el platillo asignado
    search_fields = ('business__name', 'food__name')

@admin.register(Food_Collection)
class FoodCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'complete')
    list_filter = ('complete', 'user')
