from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView

from .views import getRoutes,RetrieveUserView,RegisterUser,UsersList,BlockUser,UpdateUserView,PostsList,BlockPost,BlockedPostsList,ReportedPostsList

urlpatterns = [
    path('',getRoutes,name='getRoutes'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/me/',RetrieveUserView.as_view() ,name='getRoutes'),
    path('register/',RegisterUser.as_view(),name='register'),
    path('user-update/',UpdateUserView.as_view(), name='updateuser'),
    
    path('userslist/',UsersList.as_view(), name='userslist'),
    path('blockuser/<str:id>',BlockUser.as_view(), name='blockuser'),
    path('postslist/',PostsList.as_view(), name='postslist'),
    path('blockpost/<str:id>/',BlockPost.as_view(), name='blockpost'),    
    path('blockedposts/',BlockedPostsList.as_view(), name='blockedpostslist'),
    path('reportedposts/',ReportedPostsList.as_view(), name='reportedpostslist'),
    
]