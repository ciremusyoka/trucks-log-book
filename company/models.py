from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    main_office_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_companies")
    admins = models.ManyToManyField(User, related_name="admin_companies", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
