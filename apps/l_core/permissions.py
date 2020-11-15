from rest_framework.permissions import DjangoModelPermissions
from rest_framework import exceptions
import logging
logger = logging.getLogger(__name__)


class LCoreDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self):
        super(LCoreDjangoModelPermissions, self).__init__()

    perms_map = {
        # 'GET': ['%(app_label)s.change_%(model_name)s','%(app_label)s.view_%(model_name)s','%(app_label)s.view_self_%(model_name)s'],
        'GET': ['%(app_label)s.view_%(model_name)s','%(app_label)s.view_self_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s','%(app_label)s.change_self_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s','%(app_label)s.change_self_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s','%(app_label)s.delete_self_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)
        req_perms = [perm % kwargs for perm in self.perms_map[method]]
        logger.debug('required_permissions: %()s',req_perms)
        return req_perms

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
               or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_perms(self, perm_list, user,obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return any(user.has_perm(perm, obj) for perm in perm_list)

    def ignore_permission_method(self,request):
        ignore_permission_methods = [key for key,value in self.perms_map.items() if not  value]
        if request.method in ignore_permission_methods:
            return True


    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False

        if self.ignore_permission_method(request):
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        logger.info('requred permissions permissions :%s',perms)


        return self.has_perms(perms,request.user)



class SelfOnlyPermissions(LCoreDjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_self_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_self_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_self_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_self_%(model_name)s'],
    }
    def has_perms(self, perm_list, user,obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        print('SelfOnlyPermissions')
        print(perm_list)
        print(user.get_all_permissions())
        return all(user.has_perm(perm, obj) for perm in perm_list)