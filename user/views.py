from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .permissions import IsSelfOrReadOnly

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  permission_classes = [IsSelfOrReadOnly]

  def get_queryset(self):
    """
    Restrict users to only see their own profile.
    """
    if self.request.user.is_authenticated:
      return User.objects.filter(id=self.request.user.id)
    return User.objects.none()  # No data for unauthenticated users
