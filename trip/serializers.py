from rest_framework import serializers
from .models import Trip

class TripSerializer(serializers.ModelSerializer):
    start_date = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = "__all__"

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
        if method == "POST" and Trip.objects.filter(driver=driver, status="Ongoing").exists():
            raise serializers.ValidationError("Driver already has an ongoing trip.")

        return data

