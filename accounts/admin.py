from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TutorProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'bio', 'profile_picture')
        }),
    )

@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'hourly_rate', 'experience_years', 'is_verified', 'rating')
    list_filter = ('is_verified', 'experience_years')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')