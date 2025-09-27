from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participants = self.participants.all()
        if participants.count() == 2:
            return f"Conversation between {participants[0].username} and {participants[1].username}"
        else:
            usernames = ", ".join([user.username for user in participants[:3]])
            if participants.count() > 3:
                usernames += f" and {participants.count() - 3} others"
            return f"Group conversation: {usernames}"
    
    def get_latest_message(self):
        return self.messages.first()
    
    def get_unread_count_for_user(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def get_other_participant(self, current_user):
        """Get the other participant in a 2-person conversation"""
        other_participants = self.participants.exclude(id=current_user.id)
        if other_participants.exists():
            return other_participants.first()
        return None
    
    def get_other_participants(self, current_user):
        """Get all other participants excluding the current user"""
        return self.participants.exclude(id=current_user.id)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation's updated_at field
        self.conversation.updated_at = self.created_at
        self.conversation.save(update_fields=['updated_at'])