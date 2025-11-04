from datetime import datetime

from django.db.models import Q
from rest_framework import status
# from utils.slider_captcha import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permission.models import *
from auth.sysmenu.serializers import *
from auth.sysmenu.views import build_menu_tree
from utils.permissions import CustomPermissionMixin
from .auth import *
from .serializers import *


class LoginView(APIView):
    """
    登录视图，处理用户登录并返回 JWT token、用户信息、角色和菜单。
    """

    def get_all_menus_for_roles(self, role_ids):
        """
        获取与角色相关的所有菜单，包括子菜单和父菜单。
        :param role_ids: 角色 ID 列表
        :return: 所有关联的菜单
        """
        # 获取与角色直接关联的菜单
        menus = SysMenu.objects.filter(sysrolemenu__role__in=role_ids).distinct()

        # 用于保存最终的菜单列表
        all_menus = list(menus)

        # 获取每个菜单的所有父菜单，确保父菜单也在返回结果中
        for menu in menus:
            parent_menu_id = menu.parent_id  # 获取父菜单的ID
            while parent_menu_id:
                try:
                    parent_menu = SysMenu.objects.get(id=parent_menu_id)  # 获取父菜单对象
                    if parent_menu not in all_menus:
                        all_menus.append(parent_menu)
                    parent_menu_id = parent_menu.parent_id  # 继续往上找父菜单
                except SysMenu.DoesNotExist:
                    # 如果父菜单不存在，退出循环
                    break

        return all_menus

    def get_permissions_for_roles(self, role_ids):
        """
        获取与角色相关的所有权限。
        """
        permissions = SysRolePermission.objects.filter(role__id__in=role_ids).values_list('permission__code',
                                                                                          flat=True)
        return permissions

    def post(self, request):
        # 使用 LoginSerializer 将请求数据反序列化
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # 如果验证码功能启用，登录成功后清除验证码缓存
            if settings.CAPTCHA_ENABLED:
                captcha_key = serializer.validated_data.get('captcha_key')
                if captcha_key:
                    cache.delete(f"captcha_{captcha_key}")

            # 获取反序列化后验证成功的用户对象
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()

            # 生成 JWT token
            token = generate_jwt(user)

            # 获取用户所有角色关联的菜单，通过 ORM 进行查询，避免使用原生 SQL
            role_ids = SysRole.objects.filter(sysuserrole__user=user).values_list('id', flat=True)

            # 根据用户的角色查询对应的菜单
            menus = self.get_all_menus_for_roles(role_ids)
            permissions = self.get_permissions_for_roles(role_ids)

            # 将菜单构建为树形结构
            menu_tree = build_menu_tree(menus)

            # 序列化菜单树结构
            serializer_menu_list = SysMenuSerializer(menu_tree, many=True).data

            # 返回响应，包括 token、用户信息、角色和菜单
            return Response({
                'token': token,
                'user': UserSerializer(user).data,
                'menus': serializer_menu_list,
                'permissions': list(permissions),
                'message': '登录成功',
            })

        else:
            # 提取第一个序列化错误信息
            message = list(serializer.errors.values())[0][0]
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


# 修改密码
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'request': request})
        # 检查序列化数据是否有效
        if serializer.is_valid():
            pwd1 = serializer.validated_data.get('pwd1')
            request.user.set_password(pwd1)
            request.user.save()
            return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            message = list(serializer.errors.values())[0][0]
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


# 修改联系方式
class UpdateContactInfoView(APIView):
    def post(self, request):
        user = request.user  # 当前登录的用户
        serializer = UpdateContactInfoSerializer(user, data=request.data, partial=True)  # 允许部分更新

        if serializer.is_valid():
            serializer.save()  # 保存新的手机号和邮箱
            return Response({"message": "联系方式更新成功"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 上传头像
class ImageView(APIView):
    def post(self, request):
        # 获取上传的文件
        file = request.FILES.get('avatar')
        if file:
            # 获取文件名和后缀
            file_name = file.name
            suffixName = file_name[file_name.rfind("."):]
            # 生成新的文件名
            new_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + suffixName
            # 构造文件路径
            file_dir = os.path.join(settings.MEDIA_ROOT, 'userAvatar')
            file_path = os.path.join(file_dir, new_file_name)

            # 确保文件夹存在，如果不存在则创建
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            try:
                # 将文件写入指定路径
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                # 获取当前登录的用户
                user = request.user

                # 更新用户头像字段并保存到数据库
                user.avatar = new_file_name
                user.save()

                # 返回文件名给前端
                return Response({'message': '头像上传成功', 'file_name': new_file_name}, status=status.HTTP_200_OK)

            except Exception as e:
                # 捕获并返回异常
                return Response({'message': '上传头像失败', 'error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 当文件不存在时，返回错误响应
        return Response({'message': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)


# 用户管理视图
class UserViewSet(viewsets.ModelViewSet):
    """
    opsUser的视图，支持增删改查，并只支持按用户名过滤
    """
    queryset = opsUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'create': 'user:add',
        'update': 'user:edit',
        'destroy': 'user:delete',
        'list': 'user:list'
    }

    def get_queryset(self):
        """
        根据URL参数按用户名和状态进行过滤
        """
        # 获取查询参数
        username = self.request.query_params.get('username')
        status = self.request.query_params.get('status')

        # 初始化查询集
        queryset = super().get_queryset()

        # 使用 Q 对象进行过滤
        q_filters = Q()  # 初始化空的 Q 对象

        # 只有在参数不为空时才构造过滤条件
        if username:
            q_filters &= Q(username__icontains=username) | Q(realname__icontains=username)

        if status:
            q_filters &= Q(status=status)  # 按状态精确匹配

        # 根据过滤条件返回查询集
        queryset = queryset.filter(q_filters)

        return queryset

    def create(self, request, *args, **kwargs):
        # 提取数据
        data = request.data.copy()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)  # 序列化器验证

        # 创建用户
        user = opsUser.objects.create_user(
            username=data['username'],
            realname=data.get('realname', ''),
            email=data.get('email'),
            password=data.get('password'),  # 加密后的密码
            telephone=data.get('telephone'),
            status=data.get('status'),  # 传递用户状态
        )

        # 分配角色
        role_ids = data.get('roles', [])  # 假设请求数据中有 roles 字段，它是角色ID的列表
        for role_id in role_ids:
            try:
                role = SysRole.objects.get(id=role_id)
                SysUserRole.objects.create(user=user, role=role)  # 创建关联
            except SysRole.DoesNotExist:
                return Response({"detail": f"Role with ID {role_id} does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

        # 序列化返回创建的用户数据
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        更新用户信息并更新角色
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # 获取当前要更新的用户实例

        # 获取并验证提交的数据
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 更新用户信息
        self.perform_update(serializer)

        # 更新角色
        role_ids = request.data.get('roles', None)
        if role_ids is not None:
            # 清空当前用户的角色
            SysUserRole.objects.filter(user=instance).delete()

            # 重新分配角色
            for role_id in role_ids:
                try:
                    role = SysRole.objects.get(id=role_id)
                    SysUserRole.objects.create(user=instance, role=role)  # 创建关联
                except SysRole.DoesNotExist:
                    return Response({"detail": f"Role with ID {role_id} does not exist."},
                                    status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def get_permissions(self):
        """
        根据请求内容返回不同的权限要求
        """
        if (self.action == 'update' and
                'avatar' in self.request.data and
                len(self.request.data) == 1):
            # 头像更新只需要登录
            return [IsAuthenticated()]

        # 其他操作使用默认权限
        return super().get_permissions()

    def get_serializer_class(self):
        """
        根据请求内容返回不同的序列化器
        更新默认头像
        权限不控制
        """
        if self.action == 'update' and ('avatar' in self.request.data) and len(self.request.data) == 1:
            return AvatarUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


from utils.page import Pagination
from django.utils.dateparse import parse_datetime


class RequestLogSearchView(APIView):
    """
    提供对 RequestLog 模型的模糊搜索功能，支持在 path 和 permission_info 字段上进行匹配。
    """
    permission_classes = [CustomPermissionMixin]
    permission_code_map = {
        'list': 'requestlog:list',
    }
    pagination_class = Pagination  # 使用自定义分页器

    def get(self, request, *args, **kwargs):
        # 获取查询参数
        search_query = request.GET.get('query', '')  # 获取 'q' 参数，默认空字符串
        start_time = request.GET.get('start_time', None)  # 获取 'start_time' 参数
        end_time = request.GET.get('end_time', None)  # 获取 'end_time' 参数

        # 构建查询条件
        filter_conditions = Q()

        # 处理模糊搜索（path 和 permission_info）
        if search_query:
            filter_conditions &= (Q(path__icontains=search_query) | Q(permission_info__icontains=search_query))

        # 处理时间范围过滤
        if start_time:
            try:
                start_time = parse_datetime(start_time)  # 解析开始时间
                filter_conditions &= Q(timestamp__gte=start_time)
            except ValueError:
                return Response({"error": "Invalid start_time format"}, status=400)

        if end_time:
            try:
                end_time = parse_datetime(end_time)  # 解析结束时间
                filter_conditions &= Q(timestamp__lte=end_time)
            except ValueError:
                return Response({"error": "Invalid end_time format"}, status=400)

        # 根据过滤条件查询日志数据
        logs = RequestLog.objects.filter(filter_conditions).order_by('-timestamp')

        # 使用自定义分页器进行分页
        paginator = self.pagination_class()  # 实例化分页器
        page = paginator.paginate_queryset(logs, request)  # 获取分页数据
        if page is not None:
            # 如果有分页数据，使用序列化器返回分页后的数据
            serializer = RequestLogSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)


# 新增管理员重置视图2025-10-19
# 放在文件末尾即可
class AdminResetPasswordView(APIView):
    """
    管理员无需原密码，直接重置任意用户密码
    """
    permission_classes = [CustomPermissionMixin]
    permission_code = 'user:resetpwd'  # 与前端按钮保持一致

    def post(self, request):
        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': '密码已重置'}, status=status.HTTP_200_OK)
