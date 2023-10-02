from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response

from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Room,Message
from .serializer import *

UserModel = get_user_model()


class CreateChatRoom(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoomSerializer
 
    def post(self, request, pk):
        current_user = request.user
        other_user = UserModel.objects.get(pk=pk)

        # Check if a chat room already exists between the users
        existing_chat_rooms = Room.objects.filter(members=current_user).filter(members=other_user)
        if existing_chat_rooms.exists():
            serializer = RoomSerializer(existing_chat_rooms.first())
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create a new chat room
        chat_room = Room()
        chat_room.save()
        chat_room.members.add(current_user, other_user)
        
        serializer = RoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RoomMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
 
    def get(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
            messages = Message.objects.filter(room=room)
            serialized_messages = self.serializer_class(messages, many=True).data
            return Response(serialized_messages, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response("Room not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MesageSeenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
 
    def get(self, request, pk):
        current_user = request.user
        other_user = UserModel.objects.get(pk=pk)
        if Room.objects.filter(members=current_user).filter(members=other_user).exists():
            chat_room = Room.objects.filter(members=current_user).filter(members=other_user).first()
            messages_to_update = Message.objects.filter(Q(room=chat_room) & ~Q(sender=current_user))            
            messages_to_update.update(seen=True)            
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Chat room not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class ChatRoomListView(generics.ListAPIView):
    serializer_class = RoomListSerializer

    def get_queryset(self):
        user = self.request.user
        return Room.objects.filter(members=user)