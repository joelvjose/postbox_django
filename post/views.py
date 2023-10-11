from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions,status,generics
from django.db.models import Q

from .serializer import PostSerializer,UserSerializer,CommentSerializer,NotificationSerializer
from .models import posts,Comment,Follow,Notification
from users.models import UserAccount

class PostListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = posts.objects.all().exclude(is_deleted = True).order_by('-created_at')
    serializer_class = PostSerializer

class PostHomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    
    def get(self, request):
        try:
            user = request.user
            followers = Follow.objects.filter(follower=user)
            posts_list=[]
            print(followers)
            post_by_follower = posts.objects.none()
            if followers:
                # for fuser in followers:
                #     post_by_follower = posts.objects.filter(author=fuser.following).exclude(is_deleted = True).order_by('-created_at')
                #     posts_list.append(post_by_follower)
                following_authors = [fuser.following for fuser in followers]
                post_by_follower = posts.objects.filter(author__in=following_authors).exclude(is_deleted=True).order_by('-created_at')
            print(posts_list)
            post_by_user = posts.objects.filter(author=user).exclude(is_deleted = True).order_by('-created_at') 
            posts_list = post_by_follower | post_by_user   
            print(posts_list)
            serializer = PostSerializer(posts_list,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
# ============================================== POST SECTION =============================================
   
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
                post = serializer.save(author=user, img=img, body=body)
                for follower in user.followers.all():
                    Notification.objects.create(
                        from_user=user,
                        to_user=follower.follower,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[1][0],
                    )
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
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
            post = posts.objects.get(id=pk)
            if request.user in post.reported_users.all():
                return Response("You have already reported this post.", status=status.HTTP_200_OK)
            post.reported_users.add(request.user)                  
            return Response("Post Reported", status=status.HTTP_200_OK)
        except posts.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ============================================== FETCH POST DETAILS ============================================

class PostDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            post = posts.objects.get(id=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
# ============================================== POST LIKE SECTION =============================================

class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            user = request.user
            post = posts.objects.get(pk=pk)
            if request.user in post.likes.all():
                post.likes.remove(request.user)
                return Response("Post unliked.!", status=status.HTTP_200_OK)
            else:
                post.likes.add(request.user)
                if not post.author == user:
                    Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[0][0],
                    )       
                return Response("Post liked.!", status=status.HTTP_200_OK)
        except posts.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# ============================================== POST COMMENT SECTION =============================================

class CreateComment(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    serializer_class = CommentSerializer
    
    def post(self, request, pk, *args, **kwargs):
        try:
            user = request.user
            post = posts.objects.get(id=pk)
            body = request.data['body']
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, post_id=pk , body=body)
                Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[3][0],
                    ) 
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)  
      
class DeleteComment(APIView):
    permission_classes = [permissions.IsAuthenticated]  
    
    def delete(self,request,pk):
        try:
            comment = Comment.objects.get(id=pk,user=request.user)
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("No such comment found.!",status=status.HTTP_404_NOT_FOUND)      

# =============================================== USER PROFILE ================================================   
      
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, email, *args, **kwargs):
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
        
class MyNetworkView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        current_user = self.request.user
        followers_query = UserAccount.objects.filter(Q(followers__following=current_user) & ~Q(id=current_user.id))
        following_query = UserAccount.objects.filter(Q(following__follower=current_user) & ~Q(id=current_user.id))
        followers = UserSerializer(following_query, many=True)
        following = UserSerializer(followers_query, many=True)
        context = {
                'followers': followers.data,
                'following': following.data
            }
        return Response(context, status=status.HTTP_200_OK)
        
# ============================================== FOLLOW USER ==================================================

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            user=request.user
            follows = UserAccount.objects.get(id=pk)
            is_following = Follow.objects.filter(follower=user,following=follows)
            if is_following:
                is_following.delete()
                return Response('Unfollowed Successfully',status=status.HTTP_200_OK)
            else:
                new_follow = Follow(follower=user, following=follows)
                new_follow.save()
                Notification.objects.create(
                        from_user=user,
                        to_user=follows,
                        notification_type=Notification.NOTIFICATION_TYPES[2][0],
                    ) 
                # create new chat romm for the followers
                return Response('Followed Successfully', status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            return Response('User not found',status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# =============================================== NOTIFICATION ==================================================


class NotificationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(to_user=user).exclude(is_seen=True).order_by('-created')
    
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class NotificationsSeenView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def post(self, request, pk, *args, **kwargs):
        try:
            notification = Notification.objects.get(pk=pk)
            notification.is_seen = True
            notification.save()
            return Response(status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)
        
# =========================================== SEARCH =======================================

class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request):
        key = request.data['key']
        print(key)
        queryset = UserAccount.objects.filter(Q(username__icontains = key)|Q(first_name__icontains = key)|Q(email__icontains = key),is_admin=False)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    