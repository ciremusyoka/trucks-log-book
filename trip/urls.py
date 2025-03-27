from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, TripLogEntryViewSet

# Create a router and register the CompanyViewSet
router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trips')
router.register(r'trip-logs', TripLogEntryViewSet, basename='trip_logs')

urlpatterns = [
    path('', include(router.urls)),

]
