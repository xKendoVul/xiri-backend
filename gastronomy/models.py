from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.DecimalField(max_digits=11, decimal_places=6)
    longitude = models.DecimalField(max_digits=11, decimal_places=6)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name

class Food(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField
    image = models.ImageField(upload_to='platillos/')
    cultural_origin = models.TextField()
    department_origin = models.ForeignKey(Department, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'foods'
