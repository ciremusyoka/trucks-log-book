from django.db import models

from django.db import models

from company.models import Company, Vehicle, DriverProfile

class Trip(models.Model):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

    STATUS_CHOICES = [
        (ONGOING, "Ongoing"),
        (COMPLETED, "Completed"),
        (CANCELED, "Canceled"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name="trips")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="trips")

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    starting_location = models.JSONField()
    ending_location = models.JSONField()

    start_mileage = models.PositiveIntegerField()
    end_mileage = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ONGOING)
    manifest_no = models.CharField(max_length=100, unique=True)
    shipper = models.CharField(max_length=255)
    commodity = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Trip {self.manifest_no} - {self.status}"

