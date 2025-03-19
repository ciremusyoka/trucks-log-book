from rest_framework import permissions

class IsSelfOrReadOnly(permissions.BasePermission):
  """
  Custom permission:
  - Anyone can create a user.
  - Authenticated users can only view, update, or delete their own profile.
  """

  def has_permission(self, request, view):
    # Allow anyone to create a user
    if request.method == "POST":
        return True
    return request.user and request.user.is_authenticated

  def has_object_permission(self, request, view, obj):
    # Only allow authenticated users to access their own user data
    return obj == request.user
