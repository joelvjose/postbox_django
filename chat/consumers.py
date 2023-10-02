import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timesince import timesince

from users.models import UserAccount
from .serializer import UserSerializer
from .models import Room,Message

        
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Add the channel to the room's group
        await  self.channel_layer.group_add(self.room_group_name,self.channel_name)
        
        # Accept the WebSocket connection
        await self.accept()
        
        # Send a connection message to the client
        self.send(text_data=json.dumps({'status':'connected'}))
        
    async def disconnect(self, close_code):
        #leave group
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]
        user_serializer = UserSerializer(user)
        email = user_serializer.data['email']
        
        new_message = await self.create_message(self.room_id, message, email)
        
        # Send the received message to the room's group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'room_id': self.room_id,
                'sender_email': email,
                'created': timesince(new_message.created_at),
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        room_id = event['room_id']
        email = event['sender_email']
        created = event['created']

        # Send the chat message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'room_id': room_id,
            'sender_email': email,
            'created': created,
        }))

    @sync_to_async
    def create_message(self, room_id, message, email):
        user = UserAccount.objects.get(email=email)
        room = Room.objects.get(id=room_id) 
        message = Message.objects.create(text=message, room=room, sender=user)
        message.save()
        return message

        
        