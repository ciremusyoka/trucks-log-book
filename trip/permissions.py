from rest_framework import permissions

class IsCompanyAdminOrTripDriver(permissions.BasePermission):
    """Custom permission: Allow access to trip driver or company admin."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_company_admin = False
        is_trip_driver = False
        if getattr(obj, "company", None):
            is_company_admin = obj.company.admins.filter(id=user.id).exists()
        if getattr(obj, "driver", None):
            is_trip_driver = obj.driver.user == user
        if getattr(obj, "trip", None):
            is_company_admin = obj.trip.company.admins.filter(id=user.id).exists()
            is_trip_driver = obj.trip.driver.user == user

        return is_company_admin or is_trip_driver