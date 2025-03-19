from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    admins = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.only("id"), many=True, required=False
    )
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  # Ensures only ID is returned

    class Meta:
        model = Company
        fields = ["id", "name", "main_office_address", "phone_number", "email", "created_by", "admins", "date_created", "date_updated"]
