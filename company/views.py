from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models

from company.permissions import IsCompanyAdmin, IsDriverCompanyAdmin, IsVehicleCompanyAdmin, UserIsCompanyAdmin
from .models import Company
from .serializers import CompanySerializer
from django.shortcuts import get_object_or_404
from .models import DriverProfile
from .serializers import DriverProfileSerializer
from .models import Vehicle
from .serializers import VehicleSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        return Company.objects.filter(admins=self.request.user)

    def perform_create(self, serializer):
        company = serializer.save(created_by=self.request.user)
        company.admins.add(self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsCompanyAdmin])
    def add_admin(self, request, pk=None):
        """
        Add a user as an admin using their email (Only existing admins can do this).
        """
        company = get_object_or_404(Company, pk=pk)

        if request.user not in company.admins.all():
            return Response({"error": "Only an admin can add another admin"}, status=403)

        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = get_object_or_404(User, email=email)
        company.admins.add(user)

        return Response({"message": f"{user.email} added as an admin"}, status=200)

class DriverProfileViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsDriverCompanyAdmin, UserIsCompanyAdmin]

    def get_queryset(self):
        """Filter vehicles by company admins or assigned drivers."""
        user = self.request.user
        return (
            DriverProfile.objects.filter(
                models.Q(user=user) | models.Q(company__admins=user)
            )
            .select_related("user")
            .prefetch_related("company__admins")
            .distinct()
        )

    def perform_destroy(self, instance):
        """Soft delete a driver instead of hard deleting."""
        instance.deleted = True
        instance.save()
        return Response({"message": "Driver has been soft deleted."}, status=204)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsDriverCompanyAdmin])
    def restore(self, request, pk=None):
        """ Restore a previously soft-deleted driver profile. """
        driver = self.get_object()

        if driver.deleted:
            driver.deleted = False
            driver.save()
            return Response({"message": "Driver has been restored successfully."}, status=200)

        return Response({"message": "Driver is already active."}, status=400)
    
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """Retrieve the authenticated user's driver profile."""
        user = request.user
        driver_profile = get_object_or_404(DriverProfile, user=user, deleted=False)
        serializer = self.get_serializer(driver_profile)
        return Response(serializer.data)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVehicleCompanyAdmin, UserIsCompanyAdmin]

    def get_queryset(self):
        """Filter vehicles by company admins or assigned drivers."""
        user = self.request.user
        return Vehicle.objects.filter(
            models.Q(drivers__user=user) | models.Q(company__admins=user)
        ).distinct()

    def perform_destroy(self, instance):
        """Soft delete: Set operational to False instead of deleting."""
        instance.operational = False
        instance.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsVehicleCompanyAdmin])
    def make_operational(self, request, pk=None):
        """Endpoint to mark a vehicle as operational."""
        vehicle = self.get_object()

        if not vehicle.operational:
            vehicle.operational = True
            vehicle.save()
            return Response({"message": "Vehicle is now operational."}, status=200)

        return Response({"message": "Vehicle is already operational."}, status=400)
    
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsVehicleCompanyAdmin])
    def assign_driver(self, request, pk=None):
        """
        Assign a driver to a vehicle (Only company admins can do this).
        """
        vehicle = self.get_object()

        driver_id = request.data.get("driver_id")
        if not driver_id:
            return Response({"error": "Driver ID is required."}, status=400)

        driver = get_object_or_404(DriverProfile, id=driver_id)

        # Driver belongs to the same company?
        if driver.company != vehicle.company:
            return Response({"error": "Driver does not belong to this company."}, status=400)

        vehicle.drivers.add(driver)
        return Response({"message": f"Driver {driver.user.get_full_name()} assigned to vehicle {vehicle.truck_number}."}, status=201)
