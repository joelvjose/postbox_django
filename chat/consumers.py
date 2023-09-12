import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timesince import timesince

from users.models import UserAccount
from .serializer import UserSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Add the channel to the room's group
        await  self.channel_layer.group_add(self.room_group_name,self.channel_name)
        # Accept the WebSocket connection
        await self.accept()
        # Send a connection message to the client
        
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
                'created': timesince(new_message.timestamp),
            }
        )
        
        