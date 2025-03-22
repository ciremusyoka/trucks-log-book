from rest_framework import serializers
from .models import Trip, TripLogEntry

class TripSerializer(serializers.ModelSerializer):
    start_date = serializers.ReadOnlyField()
    last_odm_reading = serializers.SerializerMethodField()
    
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