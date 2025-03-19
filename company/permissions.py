from rest_framework import permissions

class IsCompanyAdmin(permissions.BasePermission):
    """
    Custom permission to allow only company admins to edit details and add admins.
    """
    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy", "add_admin"]:
            return request.user in obj.admins.all()  # Only admins can edit/delete
        return True
