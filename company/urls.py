from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet

# Create a router and register the CompanyViewSet
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),  # Include all viewset routes
]
