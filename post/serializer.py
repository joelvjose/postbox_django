from rest_framework import serializers

from users.models import UserAccount
from .models import posts

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'
        # fields = ['username','email','password']
        extra_kwargs={
            'password':{'write_only':True}
        }

class  PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only = True)
    
    class Meta:
        model = posts
        fields = ['body','img','author','created_time','id']