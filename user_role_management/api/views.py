from rest_framework import viewsets, status
from rest_framework.decorators import action,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Role, User
from .serializers import RoleSerializer, RoleListSerializer, UserSerializer, UserListSerializer, LoginSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
  
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(detail=False, methods=['get'])
    def role_type(self,request):
        queryset = self.get_queryset()
        serializer = RoleListSerializer(queryset, many=True)
        role_list = []
        for k in serializer.data:
            role_list.append(k['roleName'])
        return Response(role_list)

    @action(detail=True, methods=['post'])
    def update_access_modules(self, request, pk=None):
        role = self.get_object()
        new_modules = request.data.get('accessModules', [])
        role.accessModules = list(set(role.accessModules + new_modules))
        role.save()
        return Response(RoleSerializer(role).data)

    @action(detail=True, methods=['post'])
    def remove_access_module(self, request, pk=None):
        role = self.get_object()
        module = request.data.get('module')
        if module in role.accessModules:
            role.accessModules.remove(module)
            role.save()
        return Response(RoleSerializer(role).data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def list(self, request):
        queryset = self.get_queryset()
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(firstName__icontains=search) |
                Q(lastName__icontains=search) |
                Q(email__icontains=search)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Users deleted successfully"},status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        user_ids = request.data.get('user_ids', [])
        update_data = request.data.get('update_data', {})
        User.objects.filter(id__in=user_ids).update(**update_data)
        return Response({"message": "Users updated successfully"})

    @action(detail=False, methods=['post'])
    def bulk_update_different(self, request):
        updates = request.data.get('updates', [])
        for update in updates:
            User.objects.filter(id=update['id']).update(**update['data'])
        return Response({"message": "Users updated successfully"})

    @action(detail=False, methods=['post'])
    def signup(self, request):
        return self.create(request)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email=serializer.validated_data['email']
        password=serializer.validated_data['password']
        user = User.objects.get(email=email)
        if user.check_password(password):
            return Response({"message": "Login successful"})
        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def check_module_access(self, request, pk=None):
        user = self.get_object()
        module = request.query_params.get('module')
        has_access = module in user.get_access_modules()
        return Response({"has_access": has_access})