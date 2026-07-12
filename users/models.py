from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLES_CHOICES = [
        ('user', 'User / Explorador'),
        ('owner', 'Owner / Comerciante'),
        ('admin', 'Administrador'),
        ('auditor', 'Auditor de Negocios'),
    ]

    contact_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Nicaragua")
    rol = models.CharField(max_length=50, choices=ROLES_CHOICES, default='user')

    class Meta:
        db_table = "users"

class VerificationRequest(models.Model):
    STATE_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denegated', 'Denegated'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request')
    business_name = models.CharField(max_length=255)
    business_address = models.CharField(max_length=255)
    identity_document = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pendiente')
    request_date = models.DateTimeField(auto_now_add=True)
    check_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
    reviews = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "verification_request"

    def __str__(self):
        return f"Request by {self.user.username} - {self.business_name} ({self.state})"
