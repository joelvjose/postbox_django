from django.db import models
from users.models import UserAccount

# Create your models here.

class Room(models.Model):
    members = models.ManyToManyField(UserAccount,related_name='chat_room')
    
    def __str__(self):
        return ','.join([str(member) for member in self.members.all()])
    
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserAccount,on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('created_at',)
        
    def __str__(self):
        return f'{self.sender}'
