from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
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
        from django.shortcuts import get_object_or_404
        from django.contrib.auth import get_user_model
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
def edit_profile(request):
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
