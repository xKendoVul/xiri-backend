from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VerificationRequest

class PersonalisedUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser')

admin.site.register(User, PersonalisedUserAdmin)

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user','business_name','state','request_date', 'check_by')
    list_filter = ('state',)
    search_fields = ('business_name', 'user__username')

    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        for validation in queryset:
            if validation.state == 'pending':
                validation.state = 'approved'
                validation.check_by = request.user
                validation.save()

                user = validation.user
                user.rol = 'owner'
                user.save()

        self.message_user(request, "The selected request are being approved and now the users are now owners")

    approve_requests.short_description = "Mark like approved and promote users to owners"
