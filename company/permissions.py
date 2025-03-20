from rest_framework import permissions

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
            return request.user in obj.company.admins.all()  # Check if the user is an admin of the company for the driver

        return request.method in permissions.SAFE_METHODS 