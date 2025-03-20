from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company
from .models import DriverProfile

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    admins = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.only("id"), many=True, required=False
    )
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  # Ensures only ID is returned

    class Meta:
        model = Company
        fields = ["id", "name", "main_office_address", "phone_number", "email", "created_by", "admins", "date_created", "date_updated"]


class DriverProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)  # Accept email instead of user ID
    full_name = serializers.SerializerMethodField()  # Get full name from User model
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())  # Ensure company is an ID
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Track who assigned the driver

    class Meta:
        model = DriverProfile
        fields = ["id", "email", "company", "license_number", "home_terminal", "deleted", "full_name", "created_by"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def create(self, validated_data):
        email = validated_data.pop("email")
        user = User.objects.filter(email=email).first()

        try:
            deleted = validated_data.pop("deleted")
            if deleted:
                raise serializers.ValidationError({"Deleted": "Inactive drivers can not be created"})
        except:
            pass

        if not user:
            raise serializers.ValidationError({"email": "Driver with this email was not found."})

        company = validated_data["company"]
        if DriverProfile.objects.filter(user=user, company=company).exists():
            raise serializers.ValidationError("This driver is already assigned to the company.")

        return DriverProfile.objects.create(user=user, **validated_data)
