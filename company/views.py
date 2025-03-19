from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from company.permissions import IsCompanyAdmin
from .models import Company
from .serializers import CompanySerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]

    def get_queryset(self):
        return Company.objects.filter(admins=self.request.user)

    def perform_create(self, serializer):
        company = serializer.save(created_by=self.request.user)
        company.admins.add(self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsCompanyAdmin])
    def add_admin(self, request, pk=None):
        """
        Add a user as an admin using their email (Only existing admins can do this).
        """
        company = get_object_or_404(Company, pk=pk)

        if request.user not in company.admins.all():
            return Response({"error": "Only an admin can add another admin"}, status=403)

        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = get_object_or_404(User, email=email)
        company.admins.add(user)

        return Response({"message": f"{user.email} added as an admin"}, status=200)
