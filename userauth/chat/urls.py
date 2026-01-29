from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.ChatRoom, name="chat"),
    path('<str:username>/get_messages/', views.get_messages, name="get_messages"),
    path("chat/edit-chat-message/", views.edit_chat_message, name="edit_chat_message"),
    path("chat/delete-chat-message/", views.delete_chat_message, name="delete_chat_message"),
]