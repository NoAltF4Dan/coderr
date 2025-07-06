# permissions.py (or authentication/api/permissions.py)
from rest_framework import permissions

class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or view it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request for viewing *any* profile,
        # but the documentation says "Der Benutzer muss authentifiziert sein." for GET /api/profile/{pk}/
        # and "Der Benutzer kann NUR sein eigenes Profil bearbeiten." for PATCH.

        # For GET /api/profile/{pk}/, the IsAuthenticated permission on the view
        # is sufficient. This permission will mainly enforce the PATCH/PUT/DELETE.

        # Allow GET, HEAD, OPTIONS requests for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            # If the user is authenticated, they can view any profile
            return request.user.is_authenticated

        # Write permissions (PATCH) are only allowed to the owner of the profile.
        # 'obj' here is the CustomUser instance being accessed.
        return obj == request.user # Checks if the profile being accessed is the authenticated user's profile