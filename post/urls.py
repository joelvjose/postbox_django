from django.urls import path
from .views import (PostListView,PostHomeView,CreatePostView,DeletePostView,UpdatePostView,ReportPostView,
                    LikeView,ProfileView,CreateComment,DeleteComment,PostDetail,FollowUserView)

urlpatterns = [
    path('explore/', PostListView.as_view(), name='list_posts'),
    path('home/',PostHomeView.as_view(), name='explore'),
    path('create-post/', CreatePostView.as_view(), name='create-posts'),
    path('update-post/<int:pk>/', UpdatePostView.as_view(), name='update-post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete-post'),
    path('report/<int:pk>/', ReportPostView.as_view(), name='report-post'),
    
    path('like/<int:pk>/', LikeView.as_view(), name='like-post'),
    path('post-detail/<int:pk>/', PostDetail.as_view(), name='like-post'),
    path('create-comment/<int:pk>/', CreateComment.as_view(), name='add-comment'),
    path('delete-comment/<int:pk>/', DeleteComment.as_view(), name='delete-comment'),
    
    path('profile/<str:email>/', ProfileView.as_view(), name='profile'),
    path('follow-user/<int:pk>/', FollowUserView.as_view(), name='follow'),
    
]
