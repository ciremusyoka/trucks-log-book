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
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="drivers")
    license_number = models.CharField(max_length=50)
    home_terminal = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_admin")

    class Meta:
        unique_together = ("user", "company")
    
    def delete(self, *args, **kwargs):
        """ Soft delete instead of hard delete """
        self.deleted = True
        self.save()

    def __str__(self):
        return self.user.get_full_name()