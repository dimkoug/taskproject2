from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.profile == request.user.profiles


class ListRouteIsAuthenticated(permissions.BasePermission):
    """
    Custom Permission Class which authenticates a request for `list` route
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'create', 'delete', 'update']:
            # check user is authenticated for 'list' route requests
            return request.user and request.user.is_authenticated
        return True # no authentication check otherwise
