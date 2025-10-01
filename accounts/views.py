from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .profile_forms import ProfileEditForm, TutorProfileEditForm
from .models import TutorProfile

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # If user is a tutor, create their profile and redirect to completion
            if user.user_type == 'tutor':
                TutorProfile.objects.create(user=user, is_approved=False)
                login(request, user)  # Log them in first
                messages.info(
                    request, 
                    f'Welcome {username}! Please complete your tutor profile to submit your application.'
                )
                return redirect('complete_tutor_profile')
            
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile_view(request, user_id=None):
    if user_id:
        User = get_user_model()
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = request.user == profile_user
    else:
        profile_user = request.user
        is_own_profile = True
    
    # Check if profile is public or if it's the user's own profile
    if not is_own_profile and not profile_user.is_profile_public:
        messages.error(request, "This profile is private.")
        return redirect('home')
    
    tutor_profile = None
    if profile_user.user_type == 'tutor':
        try:
            tutor_profile = profile_user.tutorprofile
        except TutorProfile.DoesNotExist:
            pass
    
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'tutor_profile': tutor_profile,
        'is_own_profile': is_own_profile,
    })

@login_required
def complete_tutor_profile(request):
    """First-time tutor profile completion after signup"""
    if request.user.user_type != 'tutor':
        messages.error(request, 'This page is only for tutors.')
        return redirect('home')
    
    try:
        tutor_profile = request.user.tutorprofile
    except TutorProfile.DoesNotExist:
        tutor_profile = TutorProfile.objects.create(user=request.user, is_approved=False)
    
    # If already approved, redirect to dashboard
    if tutor_profile.is_approved:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TutorProfileEditForm(request.POST, instance=tutor_profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your tutor application has been submitted! '
                'An administrator will review your profile. You will be notified once approved.'
            )
            return redirect('tutor_pending_approval')
    else:
        form = TutorProfileEditForm(instance=tutor_profile)
    
    return render(request, 'accounts/complete_tutor_profile.html', {
        'form': form
    })

@login_required
def tutor_pending_approval(request):
    """Show pending approval page for unapproved tutors"""
    if request.user.user_type != 'tutor':
        return redirect('home')
    
    try:
        tutor_profile = request.user.tutorprofile
    except TutorProfile.DoesNotExist:
        return redirect('complete_tutor_profile')
    
    # If approved, redirect to dashboard
    if tutor_profile.is_approved:
        return redirect('dashboard')
    
    return render(request, 'accounts/tutor_pending.html', {
        'tutor_profile': tutor_profile
    })

@login_required
def edit_profile(request):
    # Check if tutor needs to complete profile first
    if request.user.user_type == 'tutor':
        try:
            tutor_profile = request.user.tutorprofile
            if not tutor_profile.is_approved:
                messages.warning(request, 'Please wait for admin approval before editing your profile.')
                return redirect('tutor_pending_approval')
        except TutorProfile.DoesNotExist:
            return redirect('complete_tutor_profile')
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        tutor_form = None
        
        if request.user.user_type == 'tutor':
            tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
            tutor_form = TutorProfileEditForm(request.POST, instance=tutor_profile)
        
        if form.is_valid() and (tutor_form is None or tutor_form.is_valid()):
            form.save()
            if tutor_form:
                tutor_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
        tutor_form = None
        
        if request.user.user_type == 'tutor':
            tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
            tutor_form = TutorProfileEditForm(instance=tutor_profile)
    
    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'tutor_form': tutor_form,
    })

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Welcome back, {username}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect unapproved tutors to pending page"""
        user = self.request.user
        if user.user_type == 'tutor':
            try:
                if not user.tutorprofile.is_approved:
                    return '/accounts/tutor/pending/'
            except TutorProfile.DoesNotExist:
                return '/accounts/tutor/complete-profile/'
        
        # Default redirect
        return super().get_success_url()

@login_required
def switch_to_tutor(request):
    """Allow students to convert their account to a tutor account"""
    if request.user.user_type == 'tutor':
        messages.info(request, 'You are already registered as a tutor.')
        try:
            if request.user.tutorprofile.is_approved:
                return redirect('dashboard')
            else:
                return redirect('tutor_pending_approval')
        except TutorProfile.DoesNotExist:
            return redirect('complete_tutor_profile')
    
    if request.method == 'POST':
        # Switch user type
        request.user.user_type = 'tutor'
        request.user.save()
        
        # Create tutor profile
        TutorProfile.objects.create(user=request.user, is_approved=False)
        
        messages.success(
            request, 
            'Your account has been converted to a tutor account! Please complete your tutor profile.'
        )
        return redirect('complete_tutor_profile')
    
    return render(request, 'accounts/switch_to_tutor.html')
