from django.contrib import admin
from .models import Department, Food

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'department_origin', 'cultural_origin')

    list_filter = ('department_origin',)
    search_fields = ('name', 'description')
