from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='Academic')
    
    def __str__(self):
        return self.name

class TutoringSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_sessions')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutor_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    duration_hours = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add the completion methods here
    def get_session_end_time(self):
        """Calculate when the session is scheduled to end"""
        if self.date_time and self.duration_hours:
            session_end = self.date_time + timedelta(hours=float(self.duration_hours))
            return session_end
        return None
    
    def can_be_completed(self):
        """Check if the session can be marked as completed"""
        if self.status != 'confirmed':
            return False
            
        session_end_time = self.get_session_end_time()
        if session_end_time:
            return timezone.now() >= session_end_time
        return False
    
    def get_time_until_completion(self):
        """Get how much time is left until the session can be completed"""
        session_end_time = self.get_session_end_time()
        if session_end_time:
            time_left = session_end_time - timezone.now()
            if time_left.total_seconds() > 0:
                return time_left
        return None
    
    def mark_as_completed(self):
        """Mark session as completed and add volunteer hours to tutor"""
        if not self.can_be_completed():
            raise ValueError("Session cannot be completed yet - it hasn't finished")
        
        # Update session status
        self.status = 'completed'
        self.save()
        
        # Add volunteer hours to tutor's profile
        tutor_profile = self.tutor.tutorprofile
        tutor_profile.volunteer_hours_completed += float(self.duration_hours)
        tutor_profile.save()
        
        return True

class Review(models.Model):
    session = models.OneToOneField(TutoringSession, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)  # Change to blank=True so it's optional
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reviewer.username} reviewed {self.reviewed.username} - {self.rating} stars"
