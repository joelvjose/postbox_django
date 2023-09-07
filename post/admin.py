from django.contrib import admin
from .models import posts,Comment,Follow

admin.site.register(posts)
admin.site.register(Comment)
admin.site.register(Follow)
