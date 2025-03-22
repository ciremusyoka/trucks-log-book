from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet

# Create a router and register the CompanyViewSet
router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trips')

urlpatterns = [
    path('', include(router.urls)),
]
