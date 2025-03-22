from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from trip.permissions import IsCompanyAdminOrTripDriver
from .models import Trip
from .serializers import TripSerializer


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

