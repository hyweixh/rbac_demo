from rest_framework.permissions import BasePermission
from auth.sysrole.models import SysUserRole
from auth.permission.models import SysRolePermission
from rest_framework.exceptions import *

class CustomPermissionDenied(APIException):
    """
    自定义异常类
    """
    status_code = 403

    def __init__(self, message):
        self.detail = {"message": message}


class CustomPermissionMixin(BasePermission):
    def has_permission(self, request, view):
        # 获取视图中的操作名称
        action = getattr(view, 'action', None) or self.get_action_from_method(request.method)

        # 获取视图的权限代码映射
        permission_code_map = getattr(view, 'permission_code_map', {})

        # 确定权限代码和消息
        permission_info = permission_code_map.get(action)
        if isinstance(permission_info, str):
            required_permission_code = permission_info
            custom_message = "您没有执行该操作的权限"  # 默认消息
        elif isinstance(permission_info, dict):
            required_permission_code = permission_info.get('code')
            custom_message = permission_info.get('message')  # 优先使用自定义消息
        else:
            return True  # 若无权限项，默认允许

        # 获取用户的角色
        user_roles = SysUserRole.objects.filter(user=request.user).values_list('role', flat=True)

        # 检查用户角色是否具备所需权限
        has_permission = SysRolePermission.objects.filter(
            role__in=user_roles,
            permission__code=required_permission_code
        ).exists()

        if not has_permission:
            raise CustomPermissionDenied(message=custom_message)

        return has_permission

    def get_action_from_method(self, method):
        """将 HTTP 方法转换为权限动作"""
        method_action_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'destroy',
            'GET': 'list',  # 通常 GET 被视为 list 或 retrieve
        }
        return method_action_map.get(method, method.lower())



