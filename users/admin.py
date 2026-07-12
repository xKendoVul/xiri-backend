from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class PersonalisedUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser')

admin.site.register(User, PersonalisedUserAdmin)
