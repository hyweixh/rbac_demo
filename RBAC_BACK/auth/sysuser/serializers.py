"""
序列化登录、用户模型
"""
from rbac_demo import settings
from rest_framework import exceptions   #异常类
from auth.sysrole.serializers import *
from django.core.cache import cache


# 登录序列化
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': '请输入用户名', 'blank': '请输入用户名',
    })
    password = serializers.CharField(required=True, allow_blank=False, max_length=100, min_length=6, error_messages={
        'required': '请输入密码', 'blank': '请输入密码',
    })

    # 滑块验证码所需
    captcha_key = serializers.CharField(required=False, allow_blank=True)
    offset_x = serializers.IntegerField(required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # 仅滑块校验
        if settings.CAPTCHA_ENABLED:
            slider_key = attrs.get('captcha_key')
            offset_x = attrs.get('offset_x')
            if not slider_key or offset_x is None:
                raise serializers.ValidationError("请完成滑动验证")

            # 优先使用预校验结果
            passed = cache.get(f'slider_pass_{slider_key}')
            if passed:
                cache.delete(f'slider_pass_{slider_key}')
            else:
                slot = cache.get(f'slider_{slider_key}')
                if not slot:
                    raise serializers.ValidationError("滑动验证已过期，请重试")

                try:
                    off = int(offset_x)
                except Exception:
                    raise serializers.ValidationError("滑动参数错误")

                true_x = int(slot['x'])
                tol = int(getattr(settings, 'CAPTCHA_TOLERANCE', 6))
                if abs(off - true_x) > tol:
                    raise serializers.ValidationError("滑动位置不准确，请重试")
                cache.delete(f'slider_{slider_key}')

        # 用户名密码校验（保持你的原逻辑）
        if username and password:
            user = opsUser.objects.filter(username=username).first()
            if not user:
                raise serializers.ValidationError("用户名不存在，请检查用户名")
            if not user.check_password(password):
                raise serializers.ValidationError("用户名或密码错误")
            if user.status == UserStatus.UNACTIVE:
                raise serializers.ValidationError("用户未激活")
            elif user.status == UserStatus.LOCKED:
                raise serializers.ValidationError("用户已锁定，请联系管理员")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("请输入用户名和密码")

        return attrs

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    class Meta:
        model = opsUser
        exclude = ['password', 'groups', 'user_permissions']    #排除不需要序列化的字段

    def get_roles(self, obj):
        """
        获取用户的所有角色信息
        """
        roles = SysUserRole.objects.filter(user=obj)
        # print('当前用户角色：',roles)
        return SysRoleSerializer([role.role for role in roles], many=True).data


#修改密码序列化
class ResetPasswordSerializer(serializers.Serializer):
    password_old = serializers.CharField(required=True,min_length=6,max_length=50)
    pwd1 = serializers.CharField(required=True,min_length=6,max_length=50)
    pwd2 = serializers.CharField(required=True,min_length=6,max_length=50)

    def validate(self, attrs):
        password_old = attrs['password_old']
        pwd1 = attrs['pwd1']
        pwd2 = attrs['pwd2']

        # 获取当前请求的用户对象
        user = self.context['request'].user
        # 验证旧密码是否匹配
        if not user.check_password(password_old):
            raise exceptions.ValidationError("旧密码错误")

        if pwd1 != pwd2:
            raise exceptions.ValidationError("两次密码输入不一致")
        elif pwd1 == password_old:
            raise exceptions.ValidationError("新密码不能与旧密码一致")
        return attrs

# 修改用户信息序列化
class UpdateContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = opsUser
        fields = ['telephone', 'email']  # 只更新电话和邮箱

    def validate_email(self, value):
        """
        自定义验证邮箱的唯一性。
        """
        # 获取当前用户的实例（假设实例是通过 context['request'].user 传入的）
        user = self.instance  # self.instance 是当前正在更新的对象

        # 如果用户没有修改邮箱，直接返回原值
        if user and user.email == value:
            return value
        if opsUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册。")
        return value

    def validate_telephone(self, value):
        """
        验证手机号是否合法。
        """
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("请输入合法的11位手机号码。")
        return value

# 更新头像序列化
class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = opsUser
        fields = ['avatar']

# 审计日志序列化
class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'

#  2025-10-19
# 放在文件末尾即可
class AdminResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, label='用户ID')
    new_password = serializers.CharField(
        required=True, min_length=6, max_length=50, label='新密码'
    )

    def validate_user_id(self, value):
        if not opsUser.objects.filter(id=value).exists():
            raise serializers.ValidationError('用户不存在')
        return value

    def save(self, **kwargs):
        user = opsUser.objects.get(id=self.validated_data['user_id'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

