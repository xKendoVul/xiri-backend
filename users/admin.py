from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VerificationRequest
from business.models import Business

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
        approved_count = 0
        for validation in queryset:
            if validation.state == 'pending':
                #Cambiar rol del usuario a owner
                user = validation.user
                user.rol = 'owner'
                user.save()

                #Crear el negocio asociado
                Business.objects.create(
                    name=validation.business_name,
                    address=validation.business_address,
                    owner=user,
                    contact_number='',  # Se completa después en el perfil del negocio
                    latitude=None,       # Se completa después
                    longitude=None       # Se completa después
                )

                #Marcar la solicitud como aprobada
                validation.state = 'approved'
                validation.check_by = request.user
                validation.save()
                approved_count += 1

        self.message_user(request, f"{approved_count} solicitud(s) aprobada(s). Los usuarios ahora son owners y sus negocios fueron creados.")

    approve_requests.short_description = "Mark like approved and promote users to owners"
