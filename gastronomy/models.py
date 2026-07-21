from django.db import models

from users.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=11, decimal_places=6)
    longitude = models.DecimalField(max_digits=11, decimal_places=6)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name

class TraditionalFood(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='platillos/')
    cultural_origin = models.TextField()
    department_origin = models.ForeignKey(Department, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'traditional_foods'

class Food_Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    traditional_food = models.ForeignKey(TraditionalFood, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'food_collection'
        unique_together = ['user', 'traditional_food']

    def __str__(self):
        return f"{self.user.username} - {self.traditional_food.name}"

class GastronomicRoute(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gastronomic_route'

    def __str__(self):
        return self.name
