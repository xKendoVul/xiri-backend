from django.contrib import admin
from .models import Department, Food, GastronomicRoute, RouteBusiness

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'department_origin', 'cultural_origin')

    list_filter = ('department_origin',)
    search_fields = ('name', 'description')

@admin.register(GastronomicRoute)
class GastronomicRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name',)

@admin.register(RouteBusiness)
class RouteBusinessAdmin(admin.ModelAdmin):
    list_display = ('route', 'business', 'suggested_order')
    list_filter = ('route',)
    ordering = ('route', 'suggested_order')
