from django.contrib import admin
from .models import Business, Menu, BusinessMenuItem, BusinessQualification, RouteBusiness

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'latitude', 'longitude', 'contact_number')
    search_fields = ('name', 'address')
    list_filter = ('owner',)

@admin.register(BusinessMenuItem)
class BusinessMenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'traditional_food', 'is_traditional_variant', 'counts_for_album')
    list_filter = ('business', 'is_traditional_variant')
    search_fields = ('name', 'business__name')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('business', 'menu_item', 'price')
    list_filter = ('business',)
    search_fields = ('business__name', 'menu_item__name')

@admin.register(BusinessQualification)
class BusinessQualificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'qualification', 'creation_date')
    list_filter = ('business', 'qualification')
    search_fields = ('user__username', 'business__name', 'comment')

@admin.register(RouteBusiness)
class RouteBusinessAdmin(admin.ModelAdmin):
    list_display = ('route', 'business', 'suggested_order')
    list_filter = ('route',)
    search_fields = ('route__name', 'business__name')
