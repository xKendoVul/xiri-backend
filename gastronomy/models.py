from django.db import models

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
    description = models.TextField()
    image = models.ImageField(upload_to='platillos/')
    cultural_origin = models.TextField()
    department_origin = models.ForeignKey(Department, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'foods'

class GastronomicRoute(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gastronomic_route'

    def __str__(self):
        return self.name

class RouteBusiness(models.Model):
    route = models.ForeignKey(GastronomicRoute, on_delete=models.CASCADE)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)
    suggested_order = models.IntegerField() # Orden que lleva la ruta

    class Meta:
        db_table = 'route_business'
        ordering = ['suggested_order']
        constraints = [
            models.UniqueConstraint(fields=['route', 'business'], name='uq_route_business')
        ]

    def __str__(self):
        return f"{self.route.name} - {self.business.name} (Order #{self.suggested_order})"
