from rest_framework import permissions
from .models import Company
from django.shortcuts import get_object_or_404

class IsCompanyAdmin(permissions.BasePermission):
    """
    Custom permission to allow only company admins to edit details and add admins.
    """
    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy", "add_admin"]:
            return request.user in obj.admins.all()  # Only admins can edit/delete
        return True

class IsDriverCompanyAdmin(permissions.BasePermission):
    """
    Custom permission to allow only company admins to edit, delete, or restore driver profiles.
    """
    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy", "restore"]:
            return request.user in obj.company.admins.all()

        return request.method in permissions.SAFE_METHODS
    

class IsVehicleCompanyAdmin(permissions.BasePermission):
    """Only company admins can update or delete vehicles."""

    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy", "make_operational", "assign_driver"]:
            return request.user in obj.company.admins.all()
        
        return request.method in permissions.SAFE_METHODS 
    

class UserIsCompanyAdmin(permissions.BasePermission):
    """Only company admins can update or delete vehicles."""

    def has_permission(self, request, view):
        company_id = request.data.get("company")
        if view.action in view.action in ["update", "partial_update", "create"] and company_id:
            company = get_object_or_404(Company, pk=company_id)
            return request.user in company.admins.all()

        return True
    
