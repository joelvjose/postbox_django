from django.contrib import admin
from .models import posts,Comment,Follow,Notification

admin.site.register(posts)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Notification)
