from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework import permissions,status,generics

from .serializer import UserSerializer,UserCreateSerializer
from post.serializer import PostSerializer
from .models import UserAccount
from post.models import posts as Post,Notification


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
        if usr.data['is_active']:
            return token
        else:
            return Response('You are Blocked by Admin',status=status.HTTP_404_NOT_FOUND)
    
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

#=================================================== UPDATE USER DETAILS =====================================
 
class UpdateUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def post(self,request):
        try:
            user = request.user
            obj = UserAccount.objects.get(id=user.id)
            serializer = self.serializer_class(instance=obj,data=request.data, partial= True) 
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.errors,status=status.HTTP_200_OK)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except UserAccount.DoesNotExist:
            return Response("User not found in the database.", status=status.HTTP_404_NOT_FOUND)
    
# ==================================================== ADMIN SIDE FUNCTIONS=============================================
class UsersList(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self,request):
        try:
            user = UserAccount.objects.filter(is_admin = False).order_by('-date_joined')
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
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PostsList(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self,request):
        try:
            posts = Post.objects.all().order_by('-created_at')
            serializer = PostSerializer(posts, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

class BlockPost(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self,request,id):
        try:
            user = request.user
            post=Post.objects.get(id=id)
            if post.is_blocked:
                post.is_blocked=False
                Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[5][0],
                    )
            else:
                post.is_blocked=True
                Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[4][0],
                    )
            post.save()
            return Response(status=status.HTTP_200_OK)
                
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BlockedPostsList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Post.objects.filter(is_blocked=True).order_by('-created_at')
    serializer_class = PostSerializer


class ReportedPostsList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Post.objects.filter(is_blocked=False, reported_users__isnull=False).order_by('-created_at')
    serializer_class = PostSerializer
