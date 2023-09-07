from rest_framework import serializers

from users.models import UserAccount
from .models import posts,Comment,Follow

class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    total_posts = serializers.SerializerMethodField()
    
    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers(self, obj):
        followers = obj.followers.all()
        follower_serializer = FollowSerializer(followers, many=True)
        return follower_serializer.data

    def get_following(self, obj):
        following = obj.following.all()
        following_serializer = FollowSerializer(following, many=True)
        return following_serializer.data
    
    def get_total_posts(self, obj):
        return obj.posts.filter(is_deleted=False).count() #posts is the related name of user in post model

    class Meta:
        model = UserAccount
        fields = ['id','username','first_name','last_name','email','display_pic',
                  'total_posts','follower_count','following_count','followers','following',
                  'last_login','is_admin','is_staff','is_active','is_superuser']
        

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    
    class Meta:
        model = Comment
        fields = ['id','user','body','created_time']
        
class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(slug_field='email', queryset=UserAccount.objects.all())
    follower = serializers.SlugRelatedField(slug_field='email', queryset=UserAccount.objects.all())
    
    class Meta:
        model = Follow
        fields = ['follower', 'following']
    
class  PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only = True)
    likes_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    comments = CommentSerializer(many = True,read_only = True)
    
    def get_likes_count(self, obj):
        return obj.total_likes()
    
    def get_reports_count(self, obj):
        return obj.total_reports()
    
    def get_followers(self, obj):
        followers = Follow.objects.filter(following=obj.author).select_related('follower')
        follower_serializer = FollowSerializer(instance=followers, many=True, context=self.context)
        return follower_serializer.data
    
    class Meta:
        model = posts
        fields = ['id','body','img','author','created_time','likes', 'likes_count','reports_count',
                  'comments','is_deleted','is_blocked','followers']