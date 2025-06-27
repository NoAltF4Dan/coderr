from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.user_type == 'business'

class IsAuthenticatedCustomer(permissions.BasePermission):
  
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "customer"


class IsAuthenticatedBusiness(permissions.BasePermission):
   
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "business"

class IsAuthenticatedCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "customer"

class IsReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
