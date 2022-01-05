from django.urls import path

from . import views

app_name = 'base'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.registrate_page, name='register'),

    path('', views.home, name='home'),

    path('profile/<str:pk>/', views.user_profile, name='user-profile'),

    path('room/<str:pk>/', views.room_page, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:pk>', views.update_room, name='update-room'),
    path('delete-room/<str:pk>', views.delete_room, name='delete-room'),

    path('delete-message/<str:pk>', views.delete_message, name='delete-message'),

    path('update-user/', views.update_user, name='update-user'),

    path('topics/', views.topics_page, name='topics'),
    path('activity/', views.activiti_page, name='activity'),
]
