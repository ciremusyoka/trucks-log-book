from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from company.permissions import IsCompanyAdmin, IsDriverCompanyAdmin
from .models import Company
from .serializers import CompanySerializer
from django.shortcuts import get_object_or_404
from .models import DriverProfile
from .serializers import DriverProfileSerializer
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

    @action(detail=True, methods=["post"], permission_classes=[IsCompanyAdmin])
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
    permission_classes = [permissions.IsAuthenticated, IsDriverCompanyAdmin]

    def get_queryset(self):
        """Only return drivers for the company where the authenticated user is an admin."""
        return DriverProfile.objects.filter(company__admins=self.request.user)

    def perform_create(self, serializer):
        """Ensure the created_by field is set and only company admins can add drivers."""
        company = serializer.validated_data["company"]

        # Ensure the user is an admin of the company
        if self.request.user not in company.admins.all():
            return Response({"error": "Only a company admin can add drivers."}, status=403)

        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete a driver instead of hard deleting."""
        instance.deleted = True
        instance.save()
        return Response({"message": "Driver has been soft deleted."}, status=204)

    @action(detail=True, methods=["post"], permission_classes=[IsDriverCompanyAdmin])
    def restore(self, request, pk=None):
        """ Restore a previously soft-deleted driver profile. """
        driver = get_object_or_404(DriverProfile, pk=pk, deleted=True)

        driver.deleted = False
        driver.save()
        return Response({"message": "Driver has been restored successfully."}, status=200)
