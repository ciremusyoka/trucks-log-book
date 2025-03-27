from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company
from .models import DriverProfile
from .models import Vehicle

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
    email = serializers.EmailField(write_only=True)
    full_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DriverProfile
        fields = ["id", "email", "company", "license_number", "company_name", "home_terminal", "deleted", "full_name", "created_by"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_company_name(self, obj):
        return obj.company.name

    def create(self, validated_data):
        email = validated_data.pop("email")
        user = User.objects.filter(email=email).first()

        if validated_data.pop("deleted", False):
            raise serializers.ValidationError({"Deleted": "Inactive drivers cannot be created."})

        if not user:
            raise serializers.ValidationError({"email": "Driver with this email was not found."})

        company = validated_data["company"]
        if DriverProfile.objects.filter(user=user, company=company).exists():
            raise serializers.ValidationError("This driver is already assigned to the company.")

        return DriverProfile.objects.create(user=user, **validated_data)


class VehicleSerializer(serializers.ModelSerializer):
    drivers = serializers.PrimaryKeyRelatedField(
        queryset=DriverProfile.objects.all(), many=True, required=False
    )
    company_admins = serializers.SerializerMethodField()
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "company",
            "drivers",
            "company_admins",
            "truck_number",
            "trailer_number",
            "license_plate",
            "state_of_registration",
            "operational",
            "created_by",
            "date_created",
            "date_updated",
        ]
        read_only_fields = ["company_admins", "created_by", "date_created", "date_updated"]

    def get_company_admins(self, obj):
        """Returns a list of company admin IDs."""
        return list(obj.company.admins.values_list("id", flat=True))

    def create(self, validated_data):
        operational = validated_data.pop("operational", True)
        drivers = validated_data.pop("drivers", [])

        if not operational:
            raise serializers.ValidationError({"operational": "A vehicle must be created as operational."})

        if drivers:
            raise serializers.ValidationError({"drivers": "Driver assignments are done after creating a vehicle"})

        validated_data["created_by"] = self.context["request"].user
        
        return Vehicle.objects.create(**validated_data) 