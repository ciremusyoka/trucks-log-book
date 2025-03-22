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

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsCompanyAdminOrTripDriver])
    def logs(self, request, pk=None):
        """Retrieve all log entries for a specific trip."""
        trip = self.get_object()
        logs = trip.log_entries.select_related("trip", "trip__driver").all()
        serializer = TripLogEntrySerializer(logs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def logs_time_series(self, request, pk=None):
        """Return grouped trip logs as a time series."""
        trip = self.get_object()
        logs = trip.log_entries.filter(deleted=False).annotate(date=TruncDate("date_created")).order_by("date_created")
        grouped_logs = {}
        previous_data = {'category': TripLogEntry.OFF_DUTY}
        log_date = None

        for log in logs:
            log_date = log.date
            if log_date not in grouped_logs:
                start_of_day = make_aware(datetime.combine(log_date, datetime.min.time()))
                previous_data['date_created'] = start_of_day
                grouped_logs[log_date] = []
            
            grouped_logs[log_date].append({
                **previous_data,
                "from": previous_data['date_created'],
                "to": log.date_created,
            })
            previous_data = log.__dict__
            previous_data.pop('_state')
        
        grouped_logs[log_date].append({
            **previous_data,
            "from": previous_data['date_created'],
            "to": make_aware(datetime.combine(log_date, datetime.max.time())),
        })

        return Response({str(date): series for date, series in grouped_logs.items()})

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
