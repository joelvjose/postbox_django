from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions,status,generics

from .serializer import PostSerializer,UserSerializer
from .models import posts
from users.models import UserAccount

class PostListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = posts.objects.all().exclude(is_deleted = True).order_by('-created_at')
    serializer_class = PostSerializer
    
class CreatePostView(APIView):
    permission_classes  = [permissions.IsAuthenticated]
    serializer_class    = PostSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            img = request.data['img']
            body = request.data['body']
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(author=user, img=img, body=body)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    
    def delete(self,request,pk):
        try:
            post = posts.objects.get(id=pk)
            post.is_deleted=True
            post.save()
            return Response(status=status.HTTP_200_OK)
        except posts.DoesNotExist:
            return Response("No such post found.!",status=status.HTTP_404_NOT_FOUND)
        
class UpdatePostView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_Class = PostSerializer
    
    def post(self,request,pk):
        try:
            user = request.user
            post_object = posts.objects.get(id=pk)
            serializer = self.serializer_Class(post_object,data=request.data,partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors)
        except posts.DoesNotExist:
            return Response("No such post found.!")
        
class ReportPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request,pk):
        try:
            post = posts.objects.get(pk=pk)
            if request.user in post.reported_by_users.all():
                return Response("You have already reported this post.", status=status.HTTP_400_BAD_REQUEST)
            post.reported_users.add(request.user)                  
            return Response("Post Reported", status=status.HTTP_200_OK)
        except posts.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            post = posts.objects.get(pk=pk)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                return Response("Post unliked.!", status=status.HTTP_200_OK)
            else:
                post.likes.add(request.user)
                return Response("Post liked.!", status=status.HTTP_200_OK)
        except posts.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, email, *args, **kwargs):
        try:
            profile = UserAccount.objects.get(email=email)
            profile_posts = posts.objects.filter(author=profile, is_deleted=False).order_by('-updated_at')
            profile_serializer = UserSerializer(profile)
            post_serializer = PostSerializer(profile_posts, many=True)

            context = {
                'profile_user': profile_serializer.data,
                'profile_posts': post_serializer.data
            }
            return Response(context, status=status.HTTP_200_OK)

        except UserAccount.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)