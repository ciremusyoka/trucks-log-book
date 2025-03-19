from django.contrib.auth.models import AbstractUser
from django.db import models

class AppUser(AbstractUser):
  email = models.EmailField(unique=True)
  phone_number = models.CharField(max_length=20, blank=False, null=False)
  first_name = models.CharField(max_length=150, null=False, blank=False)
  last_name = models.CharField(max_length=150, null=False, blank=False)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['password', 'first_name', 'last_name', 'username']

  def save(self, *args, **kwargs):
    self.username = self.email
    super().save(*args, **kwargs)

  def __str__(self):
    return self.get_full_name()
