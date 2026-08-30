from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  ROLES_CHOICES = [
    ('user', 'User / Explorador'),
    ('owner', 'Owner / Comerciante'),
    ('admin', 'Administrador'),
    ('auditor', 'Auditor de Negocios'),
  ]
  phone_regex = RegexValidator(
    regex=r'^\+?1?\d{8,15}$',
    message="El número de teléfono debe tener entre 8 y 15 dígitos, opcionalmente con +"
    )
  contact_number = models.CharField(
    max_length=20,
    blank=True,
    validators=[phone_regex]
  )
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
  id_card_number = models.CharField(max_length=15)
  identity_document = models.ImageField(upload_to='documents/id_cards')
  state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pending')
  request_date = models.DateTimeField(auto_now_add=True)
  check_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
  reviews = models.TextField(blank=True, null=True)

  class Meta:
    db_table = "verification_request"

  def __str__(self):
    return f"Request by {self.user.username} - {self.business_name} ({self.state})"
