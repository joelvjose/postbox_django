from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework import permissions,status

from .serializer import UserSerializer,UserCreateSerializer
from .models import UserAccount


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        token['email'] = user.email
        # ...
        usr = UserSerializer(user)
        if usr.data.is_active:
            return token
        else:
            return Response('User is Blocked by Admin',status=status.HTTP_404_NOT_FOUND)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'api/token/',
        'api/token/refresh/',
        'api/token/verify/',
        'users/me/',
        'register/'
    ]
    
    return Response(routes)


class RegisterUser(APIView):
    def post(self,request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        user = serializer.create(serializer.validated_data)
        user = UserSerializer(user)
        return Response(user.data,status=status.HTTP_201_CREATED)
    
class RetrieveUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user = UserSerializer(user)
        return Response(user.data, status=status.HTTP_200_OK)
    
    
class UsersList(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self,request):
        try:
            user = UserAccount.objects.filter(is_admin = False)
            serializer = UserSerializer(user, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class BlockUser(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self,request,id):
        try:
            user=UserAccount.objects.get(id=id)
            if user.is_active:
                user.is_active=False
            else:
                user.is_active=True
            user.save()
            return Response(status=status.HTTP_200_OK)
                
        except UserAccount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
