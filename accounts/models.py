from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=1000, blank=True)  # Increased from 500
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    birthday = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Enhanced profile fields
    location = models.CharField(max_length=100, blank=True, help_text="City, Province")
    school = models.CharField(max_length=200, blank=True, help_text="School or University name")
    grade_level = models.CharField(max_length=50, blank=True, help_text="Grade 9, Grade 12, University, etc.")
    interests = models.TextField(max_length=500, blank=True, help_text="Hobbies, interests, goals")
    social_linkedin = models.URLField(blank=True)
    social_instagram = models.CharField(max_length=100, blank=True, help_text="Instagram username")
    is_profile_public = models.BooleanField(default=True, help_text="Show profile to other users")
    
    def get_age(self):
        if self.birthday:
            from datetime import date
            today = date.today()
            return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return None

class TutorProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Less than 1 year'),
        ('intermediate', '1-3 years'),
        ('experienced', '3-5 years'),
        ('expert', '5+ years'),
    ]
    
    TEACHING_STYLE_CHOICES = [
        ('visual', 'Visual Learning'),
        ('hands_on', 'Hands-on Practice'),
        ('discussion', 'Discussion Based'),
        ('structured', 'Structured Lessons'),
        ('flexible', 'Flexible Approach'),
    ]
    
    # Core fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField('tutoring.Subject')
    experience_years = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    availability = models.TextField(help_text="Describe your availability")
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    # Volunteer tracking fields (replacing payment fields)
    volunteer_hours_completed = models.PositiveIntegerField(
        default=0, 
        help_text="Total volunteer hours completed"
    )
    volunteer_hours_goal = models.PositiveIntegerField(
        default=10, 
        help_text="Monthly volunteer hours goal"
    )
    volunteer_start_date = models.DateField(
        auto_now_add=True,
        help_text="When they started volunteering"
    )
    
    # Enhanced teaching fields
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    teaching_style = models.CharField(max_length=20, choices=TEACHING_STYLE_CHOICES, default='flexible')
    certifications = models.TextField(blank=True, help_text="Teaching certifications, degrees, etc.")
    specializations = models.TextField(blank=True, help_text="Special areas of expertise")
    teaching_philosophy = models.TextField(max_length=1000, blank=True, help_text="Your approach to teaching")
    languages_spoken = models.CharField(max_length=200, default="English", help_text="Languages you can teach in")
    
    # Volunteer motivation and commitment
    motivation = models.TextField(
        max_length=1000, 
        blank=True, 
        help_text="Why do you want to volunteer as a tutor?"
    )
    commitment_level = models.CharField(
        max_length=20,
        choices=[
            ('casual', 'Casual (1-2 hours/week)'),
            ('regular', 'Regular (3-5 hours/week)'),
            ('dedicated', 'Dedicated (6-10 hours/week)'),
            ('intensive', 'Intensive (10+ hours/week)'),
        ],
        default='regular',
        help_text="How much time can you commit weekly?"
    )
    
    # Availability preferences
    prefers_online = models.BooleanField(default=True)
    prefers_in_person = models.BooleanField(default=False)
    travel_distance = models.IntegerField(default=0, help_text="Max km willing to travel (0 for online only)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Volunteer Tutor"
    
    def get_completion_rate(self):
        """Calculate percentage of monthly goal completed"""
        if self.volunteer_hours_goal > 0:
            return min(100, (self.volunteer_hours_completed / self.volunteer_hours_goal) * 100)
        return 0
    
    def get_volunteer_level(self):
        """Get volunteer level based on hours completed"""
        hours = self.volunteer_hours_completed
        if hours >= 100:
            return "Master Volunteer"
        elif hours >= 50:
            return "Expert Volunteer"
        elif hours >= 25:
            return "Experienced Volunteer"
        elif hours >= 10:
            return "Active Volunteer"
        else:
            return "New Volunteer"
