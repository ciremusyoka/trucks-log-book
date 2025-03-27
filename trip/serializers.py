from rest_framework import serializers

from company.models import Company, DriverProfile, Vehicle
from .models import Trip, TripLogEntry

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "main_office_address"]

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ["id", "home_terminal", "license_number"]

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "license_plate", "truck_number", "license_plate"]

class TripSerializer(serializers.ModelSerializer):
    start_date = serializers.ReadOnlyField()
    last_odm_reading = serializers.SerializerMethodField()
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), write_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), write_only=True)
    driver = serializers.PrimaryKeyRelatedField(queryset=DriverProfile.objects.all(), write_only=True)
    
    class Meta:
        model = Trip
        fields = "__all__"

    def get_last_odm_reading(self, obj):
        """Fetch the latest odm_reading from trip logs."""
        last_log = (
            TripLogEntry.objects.filter(trip=obj, odm_reading__isnull=False)
            .order_by("-date_created")
            .first()
        )
        return last_log.odm_reading if last_log else None

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")

        user = request.user
        method = request.method
        instance = self.instance

        company = data.get("company", instance.company if instance else None)
        driver = data.get("driver", instance.driver if instance else None)
        vehicle = data.get("vehicle", instance.vehicle if instance else None)

        # Is a company admin or the driver of the trip?
        if not (company.admins.filter(id=user.id).exists() or user == driver.user):
            raise serializers.ValidationError("You must be a company admin or the assigned driver.")

        # Belongs to the company?
        if driver.company != company:
            raise serializers.ValidationError("Driver must belong to the company.")

        # Assigned to the vehicle?
        if not vehicle.drivers.filter(id=driver.id).exists():
            raise serializers.ValidationError("Driver must be assigned to the vehicle.")

        # Has ongoing trip?
        if method == "POST":
            if Trip.objects.filter(driver=driver, status="Ongoing").exists():
                raise serializers.ValidationError("Driver already has an ongoing trip.")
            
            if Trip.objects.filter(vehicle=vehicle, status="Ongoing").exists():
                raise serializers.ValidationError("Truck already has an ongoing trip.")

        return data
    
    def to_representation(self, instance):
        """Use nested serializers when returning data (GET requests)."""
        representation = super().to_representation(instance)
        representation["vehicle"] = VehicleSerializer(instance.vehicle).data
        representation["company"] = CompanySerializer(instance.company).data
        representation["driver"] = DriverSerializer(instance.driver).data
        return representation


class TripLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLogEntry
        fields = "__all__"

    def validate(self, data):
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")

        user = request.user
        instance = self.instance

        trip = data.get("trip", instance.trip if instance else None)
        category = data.get("category", instance.category if instance else None)
        odm_reading = data.get("odm_reading", instance.odm_reading if instance else None)

        if not trip:
            raise serializers.ValidationError("Trip is required.")

        # Is trip driver or a company admin?
        if not (trip.driver.user == user or trip.company.admins.filter(id=user.id).exists()):
            raise serializers.ValidationError("You must be the trip driver or a company admin.")

        # `odm_reading` is provided for `SLEEPER_BERTH`?
        if category in {TripLogEntry.SLEEPER_BERTH, TripLogEntry.OFF_DUTY} and odm_reading is None:
            raise serializers.ValidationError(f"Odometer reading is required for {category}.")

        return data