from rest_framework import permissions
from .models import UserProfile

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role == 'admin'
        except UserProfile.DoesNotExist:
            return False  
        
class IsAnalyst(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role == 'analyst'
        except UserProfile.DoesNotExist:
            return False  