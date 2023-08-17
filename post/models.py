from django.db import models
from users.models import UserAccount
from django.utils.timesince import timesince

# Create your models here.

class posts(models.Model):
    body        = models.TextField(blank=True, null=True)
    author      = models.ForeignKey(UserAccount,related_name='posts',on_delete=models.CASCADE)
    img         = models.ImageField(upload_to='posts/')
    likes       = models.ManyToManyField(UserAccount,related_name='liked_posts',blank=True) 
    
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=False)
    
    def __str__(self):
        return self.author.username

    def total_likes(self):
        return self.likes.count()
    
    def created_time(self):
        return timesince(self.created_at)