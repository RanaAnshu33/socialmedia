'''
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_name")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_name")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    is_seen = models.BooleanField(default=False)   

    def __str__(self):
        return f"{self.sender} - {self.receiver}"
'''
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_name")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_name")
    content = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.receiver}"

