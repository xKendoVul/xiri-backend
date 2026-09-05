from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from users.models import User

class Business(models.Model):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(
            max_length=20,
            blank=True,
            validators=[RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message="Número de teléfono inválido"
            )]
        )
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=6, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business'

class BusinessMenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='menu_items')

    traditional_food = models.ForeignKey(
        'gastronomy.TraditionalFood',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_variations'
    )

    is_traditional_variant = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business_menu_item'

    def __str__(self):
        return f"{self.name} - {self.business.name}"

    @property
    def counts_for_album(self):
        return self.traditional_food is not None or self.is_traditional_variant

class Menu(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(BusinessMenuItem, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'menu'
        unique_together = ['business', 'menu_item']

    def __str__(self):
        return f"{self.menu_item.name} - {self.business.name} ({self.price} C$)"

class BusinessQualification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    qualification = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField(blank=True, null=True)

    evidence_image = models.ImageField(upload_to='reviews/evidence/', blank=False, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "business_qualification"
        constraints = [
            models.UniqueConstraint(
                fields=['user','business'],
                name='unique_user_business_qualification'
            )
        ]

    def __str__(self):
        return f"{self.user.username} in {self.business.name} ({self.qualification})"


class RouteBusiness(models.Model):
    route = models.ForeignKey('gastronomy.GastronomicRoute', on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    suggested_order = models.IntegerField()

    class Meta:
        db_table = 'route_business'
        ordering = ['suggested_order']
        constraints = [
            models.UniqueConstraint(fields=['route', 'business'], name='uq_route_business')
        ]

    def __str__(self):
        return f"{self.route.name} - {self.business.name} (Order #{self.suggested_order})"
