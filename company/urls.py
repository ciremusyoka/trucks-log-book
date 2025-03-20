from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DriverProfileViewSet, VehicleViewSet

# Create a router and register the CompanyViewSet
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'drivers', DriverProfileViewSet, basename='driver')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')

urlpatterns = [
    path('', include(router.urls)),
]
