"""
Custom permissions for chat microservice
"""
from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    """
    Permission untuk admin dan staff saja
    """
    
    def has_permission(self, request, view):
        """
        Check if user is admin or staff
        """
        if not request.user or not hasattr(request.user, 'role'):
            return False
            
        return request.user.role in ['admin', 'staff']


class IsOwnerOrAdmin(BasePermission):
    """
    Permission untuk owner object atau admin
    """
    
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'id'))
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user owns the object or is admin
        """
        # Admin dan staff bisa akses semua
        if hasattr(request.user, 'role') and request.user.role in ['admin', 'staff']:
            return True
            
        # Owner bisa akses objectnya sendiri
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
            
        return False


class IsBuyerOnly(BasePermission):
    """
    Permission untuk buyer saja (tidak bisa admin/staff)
    """
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'role'):
            return False
            
        return request.user.role == 'buyer'