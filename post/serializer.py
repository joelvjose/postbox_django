from rest_framework import serializers

from users.models import UserAccount
from .models import posts

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id','username','first_name','last_name','email','display_pic',
                  'last_login','is_admin','is_staff','is_active','is_superuser']

class  PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only = True)
    likes_count = serializers.SerializerMethodField()
    reports_count = serializers.SerializerMethodField()
    
    def get_likes_count(self, obj):
        return obj.total_likes()
    
    def get_reports_count(self, obj):
        return obj.total_reports()
    
    class Meta:
        model = posts
        fields = ['id','body','img','author','created_time','likes', 'likes_count','reports_count']