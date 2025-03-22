from django.db.models import Q
from django.db.models.functions import TruncDate
from django.utils.timezone import make_aware

from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from trip.permissions import IsCompanyAdminOrTripDriver
from .models import Trip
from .serializers import TripSerializer
from .models import TripLogEntry
from .serializers import TripLogEntrySerializer

from datetime import datetime


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdminOrTripDriver]

    def get_queryset(self):
        """Driver or company admin trips."""
        user = self.request.user

        return Trip.objects.filter(
            Q(driver__user=user) | Q(company__admins=user)
        ).distinct().select_related("driver", "company").prefetch_related("company__admins")

    def perform_destroy(self, instance):
        """Soft delete the trip."""
        instance.deleted = True
        instance.save()


class TripLogEntryViewSet(viewsets.ModelViewSet):
    """Manage trip log entries, accessible only by trip drivers or company admins."""
    queryset = TripLogEntry.objects.all()
    serializer_class = TripLogEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdminOrTripDriver]

    def get_queryset(self):
        """Filter logs to only those related to the authenticated user's trips."""
        user = self.request.user
        return TripLogEntry.objects.filter(
            Q(trip__driver__user=user) | 
            Q(trip__company__admins=user)
        ).distinct() 

    def perform_create(self, serializer):
        """Ensure the user is authorized to create a log entry."""
        trip = serializer.validated_data.get("trip")

        if not (trip.driver.user == self.request.user or trip.company.admins.filter(id=self.request.user.id).exists()):
            raise PermissionDenied("You must be the trip driver or a company admin.")

        serializer.save()
