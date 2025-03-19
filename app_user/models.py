from django.contrib.auth.models import AbstractUser
from django.db import models

class AppUser(AbstractUser):
  username = None  # Remove username field
  email = models.EmailField(unique=True)
  phone_number = models.CharField(max_length=20, blank=True, null=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['password', 'first_name', 'last_name']

  def __str__(self):
    return self.get_full_name()
