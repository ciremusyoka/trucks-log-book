from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DriverProfileViewSet

# Create a router and register the CompanyViewSet
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'drivers', DriverProfileViewSet, basename='driver')

urlpatterns = [
    path('', include(router.urls)),
]
