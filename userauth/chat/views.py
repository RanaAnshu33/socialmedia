from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import  ChatMessage
from userauth.models import Profile
from django.db.models import Q
from django.utils.dateformat import DateFormat
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required(login_url='loginn')
@login_required
def ChatRoom(request, username):
    r = User.objects.filter(username=username).first()
    messages = ChatMessage.objects.filter((Q(sender=request.user) & Q(receiver=r)) |(Q(sender=r) & Q(receiver=request.user))).order_by("timestamp")
    ChatMessage.objects.filter(sender=r,receiver=request.user,is_seen=False).update(is_seen=True)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        msg = request.POST.get('msg')
        if msg:
            ChatMessage.objects.create(sender=request.user,receiver=r,content=msg)

    return render(request,"chat/chat.html",{"r": r, "messages": messages, "profile": profile})


@login_required
def get_messages(request, username):
    r = User.objects.filter(username=username).first()

    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=r)) |
        (Q(sender=r) & Q(receiver=request.user))
    ).order_by("timestamp")

    messages_data = [
        {
            "sender": message.sender.username,
            "content": message.content,
            "timestamp": DateFormat(message.timestamp).format('H:i'),
            "is_seen": message.is_seen   
        }
        for message in messages
    ]

    return JsonResponse({"messages": messages_data})


# def delete_message(request, id):
#     message = get_object_or_404(ChatMessage, id=id)
#     if message.sender == request.user:
#         message.delete()
#     return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def edit_chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg_id = data.get("id")
        new_content = data.get("content")

        message = get_object_or_404(
            ChatMessage,
            id=msg_id,
            sender=request.user
        )

        message.content = new_content
        message.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def delete_chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg_id = data.get("id")

        message = get_object_or_404(
            ChatMessage,
            id=msg_id,
            sender=request.user
        )
        message.delete()

        return JsonResponse({"status": "deleted"})

    return JsonResponse({"error": "Invalid request"}, status=400)
