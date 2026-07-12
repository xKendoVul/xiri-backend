from django.db import models
from users.models import User
from gastronomy.models import Food

# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=11, decimal_places=6)
    longitude = models.DecimalField(max_digits=11, decimal_places=6)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'business'

class Menu(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'menu'

class Food_Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'food_collection'

    def __str__(self):
        return f"{self.user.username} - {self.food.name}"

class BusinessQualification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    qualification = models.IntegerField
    comment = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "business_qualification"

    def __str__(self):
        return f"{self.user.username} in {self.business.name} ({self.qualification})"
