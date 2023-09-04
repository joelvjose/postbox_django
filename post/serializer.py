from rest_framework import serializers

from users.models import UserAccount
from .models import posts,Comment

class UserSerializer(serializers.ModelSerializer):
    total_posts = serializers.SerializerMethodField()
    
    def get_total_posts(self, obj):
        return obj.posts.filter(is_deleted=False).count() #posts is the related name of user in post model

    class Meta:
        model = UserAccount
        fields = ['id','username','first_name','last_name','email','display_pic',
                  'total_posts',
                  'last_login','is_admin','is_staff','is_active','is_superuser']
        

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    
    class Meta:
        model = Comment
        fields = ['id','user','body','created_time']
    
class  PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only = True)
    likes_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many = True,read_only = True)
    
    def get_likes_count(self, obj):
        return obj.total_likes()
    
    def get_reports_count(self, obj):
        return obj.total_reports()
    
    class Meta:
        model = posts
        fields = ['id','body','img','author','created_time','likes', 'likes_count','reports_count','comments']