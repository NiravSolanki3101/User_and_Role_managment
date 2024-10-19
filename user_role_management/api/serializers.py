from rest_framework import serializers
from .models import Role, User

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'roleName', 'accessModules', 'createdAt', 'active']

class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['roleName']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', write_only=True)
    roleName = serializers.CharField(source='get_role_name', read_only=True)
    accessModules = serializers.ListField(source='get_access_modules', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'email', 'password', 'role', 'role_id','roleName', 'accessModules']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    roleName = serializers.CharField(source='get_role_name')
    accessModules = serializers.ListField(source='get_access_modules')

    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'email', 'roleName', 'accessModules']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()