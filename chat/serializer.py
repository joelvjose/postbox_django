from rest_framework import serializers
from django.utils.timesince import timesince

from .models import Message,Room
from users.models import UserAccount

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_image']