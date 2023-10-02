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
    is_blocked = models.BooleanField(default=False)
    reported_users = models.ManyToManyField(UserAccount, related_name='reported_posts', blank=True)
    
    def __str__(self):
        return self.author.username

    def total_likes(self):
        return self.likes.count()
    
    def created_time(self):
        return timesince(self.created_at)
    
    def total_reports(self):
        return self.reported_users.count()
    
class Comment(models.Model):
    post = models.ForeignKey(posts,related_name='comments',on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s - %s - %s' % (self.post.id,self.body, self.user.first_name)
    
    def created_time(self):
        return timesince(self.created_at)
    
class Follow(models.Model):
    follower = models.ForeignKey(UserAccount, related_name='followers', on_delete=models.CASCADE)
    following = models.ForeignKey(UserAccount, related_name='following', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.follower} -> {self.following}'
    
class Notification(models.Model):
   NOTIFICATION_TYPES = [
        ('like', 'New Like'),
        ('post', 'New Post'),
        ('follow', 'New Follow'),
        ('comment', 'New Comment'),
        ('blocked', 'Post Blocked'),
        ('unblocked', 'Post Unblocked'),
    ]
   
   from_user = models.ForeignKey(UserAccount, related_name="notification_from", on_delete=models.CASCADE, null=True)
   to_user = models.ForeignKey(UserAccount, related_name="notification_to", on_delete=models.CASCADE, null=True)
   notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
   post  = models.ForeignKey('posts', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
   comment  = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
   created = models.DateTimeField(auto_now_add=True)
   is_seen = models.BooleanField(default=False)
   
   def __str__(self):
        return f"{self.from_user} sent a {self.notification_type} notification to {self.to_user}"