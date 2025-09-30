from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    established_year = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Car Model model
class CarModel(models.Model):
    # Limited type choices
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    COUPE = 'Coupe'
    HATCHBACK = 'Hatchback'
    TRUCK = 'Truck'
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (COUPE, 'Coupe'),
        (HATCHBACK, 'Hatchback'),
        (TRUCK, 'Truck'),
    ]

    # Many-to-one to CarMake (one make -> many models)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')

    # Dealer Id refers to a dealer created in the external reviews DB
    dealer_id = models.IntegerField(help_text="Refers to dealer ID in the external database")

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=SEDAN)

    # Year constrained as specified
    year = models.IntegerField(
        validators=[MinValueValidator(2015), MaxValueValidator(2023)]
    )

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate entries for the same make/model/year
        unique_together = ('make', 'name', 'year')

    def __str__(self):
        return f"{self.make.name} {self.name} ({self.year})"
