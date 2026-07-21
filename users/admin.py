from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VerificationRequest

class PersonalisedUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser')

admin.site.register(User, PersonalisedUserAdmin)

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """
    Admin básico para VerificationRequest.
    
    La lógica de aprobación/rechazo está en el ViewSet (API).
    """
    list_display = ('user', 'business_name', 'state', 'request_date', 'check_by')
    list_filter = ('state',)
    search_fields = ('business_name', 'user__username')
    readonly_fields = ('request_date', 'check_by', 'user')
