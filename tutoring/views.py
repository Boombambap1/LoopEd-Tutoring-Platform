from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from .models import Subject, TutoringSession, Review
from accounts.models import User, TutorProfile
from .forms import TutorSearchForm, BookingForm

def home(request):
    subjects = Subject.objects.all()[:6]  # Show first 6 subjects
    featured_tutors = TutorProfile.objects.filter(is_verified=True)[:6]
    return render(request, 'tutoring/home.html', {
        'subjects': subjects,
        'featured_tutors': featured_tutors
    })

def tutor_search(request):
    form = TutorSearchForm(request.GET or None)
    tutors = TutorProfile.objects.filter(is_verified=True)
    
    if form.is_valid():
        subject = form.cleaned_data.get('subject')
        location = form.cleaned_data.get('location')
        max_rate = form.cleaned_data.get('max_rate')
        
        if subject:
            tutors = tutors.filter(subjects=subject)
        if max_rate:
            tutors = tutors.filter(hourly_rate__lte=max_rate)
        # Location filtering can be added later
    
    return render(request, 'tutoring/tutor_search.html', {
        'form': form,
        'tutors': tutors
    })

def tutor_detail(request, tutor_id):
    tutor_profile = get_object_or_404(TutorProfile, id=tutor_id)
    reviews = Review.objects.filter(reviewed=tutor_profile.user).order_by('-created_at')[:5]
    return render(request, 'tutoring/tutor_detail.html', {
        'tutor': tutor_profile,
        'reviews': reviews
    })

@login_required
def book_session(request, tutor_id):
    tutor_profile = get_object_or_404(TutorProfile, id=tutor_id)
    
    # Check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can book tutoring sessions.')
        return redirect('tutor_detail', tutor_id=tutor_id)
    
    if request.method == 'POST':
        form = BookingForm(tutor_profile, request.POST)
        if form.is_valid():
            # Create the tutoring session
            session = TutoringSession.objects.create(
                student=request.user,
                tutor=tutor_profile.user,
                subject=form.cleaned_data['subject'],
                date_time=datetime.combine(
                    form.cleaned_data['preferred_date'],
                    form.cleaned_data['preferred_time']
                ),
                duration_hours=form.cleaned_data['duration_hours'],
                notes=form.cleaned_data['notes'],
                status='pending'
            )
            
            messages.success(
                request, 
                f'Session booking request sent to {tutor_profile.user.get_full_name()}! '
                f'You can track the status in your dashboard.'
            )
            return redirect('dashboard')
    else:
        form = BookingForm(tutor_profile)
    
    return render(request, 'tutoring/book_session.html', {
        'tutor': tutor_profile,
        'form': form
    })

@login_required
def dashboard(request):
    if request.user.user_type == 'tutor':
        sessions = TutoringSession.objects.filter(tutor=request.user).order_by('-date_time')
        try:
            tutor_profile = request.user.tutorprofile
        except:
            tutor_profile = None
    else:
        sessions = TutoringSession.objects.filter(student=request.user).order_by('-date_time')
        tutor_profile = None
    
    return render(request, 'tutoring/dashboard.html', {
        'sessions': sessions,
        'tutor_profile': tutor_profile
    })

@login_required
def session_action(request, session_id, action):
    session = get_object_or_404(TutoringSession, id=session_id)
    
    # Check permissions
    if action in ['accept', 'reject'] and request.user != session.tutor:
        messages.error(request, "You can only manage your own tutoring sessions.")
        return redirect('dashboard')
    
    if action == 'cancel' and request.user not in [session.student, session.tutor]:
        messages.error(request, "You can only cancel sessions you're involved in.")
        return redirect('dashboard')
    
    # Perform actions
    if action == 'accept':
        session.status = 'confirmed'
        session.save()
        messages.success(request, f'Session with {session.student.get_full_name()} has been confirmed!')
    
    elif action == 'reject':
        session.status = 'cancelled'
        session.save()
        messages.warning(request, f'Session with {session.student.get_full_name()} has been declined.')
    
    elif action == 'cancel':
        if session.status in ['pending', 'confirmed']:
            session.status = 'cancelled'
            session.save()
            if request.user == session.student:
                messages.success(request, 'Your session has been cancelled.')
            else:
                messages.success(request, 'Session has been cancelled.')
        else:
            messages.error(request, 'This session cannot be cancelled.')
    
    elif action == 'complete':
        if request.user == session.tutor and session.status == 'confirmed':
            try:
                session.mark_as_completed()
                messages.success(request, f'Session completed! {session.duration_hours} volunteer hours added to your profile.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Only the tutor can mark confirmed sessions as completed.')
    
    return redirect('dashboard')

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(TutoringSession, id=session_id)
    
    # Check if user is involved in this session
    if request.user not in [session.student, session.tutor]:
        messages.error(request, "You don't have permission to view this session.")
        return redirect('dashboard')
    
    return render(request, 'tutoring/session_detail.html', {
        'session': session
    })

# New time-based completion views
@login_required
def complete_session(request, session_id):
    session = get_object_or_404(TutoringSession, id=session_id, tutor=request.user)
    
    if request.method == 'POST':
        try:
            session.mark_as_completed()
            messages.success(request, f'Session completed! {session.duration_hours} volunteer hours added to your profile.')
            return redirect('dashboard')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('session_detail', session_id=session_id)
    
    # For GET requests, return JSON with completion status
    return JsonResponse({
        'can_complete': session.can_be_completed(),
        'time_left': str(session.get_time_until_completion()) if session.get_time_until_completion() else None,
        'session_end_time': session.get_session_end_time().isoformat() if session.get_session_end_time() else None
    })

@login_required
def check_completion_status(request, session_id):
    """AJAX endpoint to check if session can be completed"""
    session = get_object_or_404(TutoringSession, id=session_id, tutor=request.user)
    
    time_left = session.get_time_until_completion()
    
    return JsonResponse({
        'can_complete': session.can_be_completed(),
        'time_left_seconds': int(time_left.total_seconds()) if time_left else 0,
        'time_left_display': str(time_left).split('.')[0] if time_left else "Session completed",
        'session_end_time': session.get_session_end_time().strftime('%B %d, %Y at %I:%M %p') if session.get_session_end_time() else None
    })