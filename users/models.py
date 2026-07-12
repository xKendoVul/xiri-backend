from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    contact_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Nicaragua")
    rol = models.CharField(max_length=50, default="Explorer")

    class Meta:
        db_table = "users"
