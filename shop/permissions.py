from rest_framework import permissions

class IsAdminOrWriteOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            if request.method == 'GET':
                return request.user.is_superuser
            else:
                return True
        elif request.method == 'POST':
            return True
        else:
            return False
            

class UserPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in ['HEAD', 'OPTIONS']:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        elif request.method == 'PUT' or request.method == 'PATCH':
            return obj == request.user or request.user.is_superuser
        elif request.method == 'DELETE':
            return obj == request.user or request.user.is_superuser
        else:
            return False