from django.contrib import admin
from .models import Subject, TutoringSession, Review

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(TutoringSession)
class TutoringSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'subject', 'date_time', 'status')
    list_filter = ('status', 'subject', 'date_time')
    search_fields = ('student__username', 'tutor__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
