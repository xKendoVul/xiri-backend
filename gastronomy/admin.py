from django.contrib import admin
from .models import Department, TraditionalFood, GastronomicRoute, FoodCollection

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(TraditionalFood)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'department_origin', 'cultural_origin')
    list_filter = ('department_origin',)
    search_fields = ('name', 'description')

@admin.register(FoodCollection)
class FoodCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'traditional_food', 'complete', 'registered_date')
    list_filter = ('complete', 'user')
    search_fields = ('user__username', 'traditional_food__name')

@admin.register(GastronomicRoute)
class GastronomicRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description')
    list_filter = ('department',)
    search_fields = ('name', 'description')
