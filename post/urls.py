from django.urls import path
from .views import (PostListView,CreatePostView,DeletePostView,UpdatePostView)

urlpatterns = [
    path('', PostListView.as_view(), name='list_posts'),
    path('create-post/', CreatePostView.as_view(), name='create-posts'),
    path('update-post/<int:pk>/', UpdatePostView.as_view(), name='update-post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete-post'),
]
