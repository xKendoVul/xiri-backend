from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
  def has_permission(self, request, view):
		# Primero: debe estar autenticado
			if not request.user or not request.user.is_authenticated:
				return False

		# (GET) solo autenticados
			if request.method in permissions.SAFE_METHODS:
				return True

		# (POST/PUT/DELETE): solo admins
			return request.user.rol == 'admin' or request.user.is_superuser

class IsOwnerOrAdmin(permissions.BasePermission):
	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False

		if request.method in permissions.SAFE_METHODS:
			return True  # Usuarios autenticados ven la lista

		# Solo owners o admins pueden crear/modificar
		return request.user.rol in ['owner', 'admin'] or request.user.is_superuser

class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return bool(request.user and request.user.is_authenticated and (request.user.rol == 'admin' or request.user.is_superuser))
