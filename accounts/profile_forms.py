from django import forms
from .models import User, TutorProfile

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'bio',
            'profile_picture', 'location', 'school', 'grade_level',
            'interests', 'social_linkedin', 'social_instagram', 'is_profile_public'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (123) 456-7890'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell others about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vancouver, BC'}),
            'school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your school or university'}),
            'grade_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grade 10, University Year 2, etc.'}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your hobbies, interests, and goals...'}),
            'social_linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourname'}),
            'social_instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your_username'}),
            'is_profile_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TutorProfileEditForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    class Meta:
        model = TutorProfile
        fields = [
            'subjects', 'experience_years', 'education',
            'experience_level', 'teaching_style', 'certifications',
            'specializations', 'teaching_philosophy', 'languages_spoken',
            'availability', 'motivation', 'commitment_level', 'volunteer_hours_goal',
            'prefers_online', 'prefers_in_person', 'travel_distance'
        ]
        widgets = {
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '50'}),
            'education': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your educational background'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'teaching_style': forms.Select(attrs={'class': 'form-select'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Teaching certifications, degrees, etc.'}),
            'specializations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special areas of expertise...'}),
            'teaching_philosophy': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your approach to teaching...'}),
            'languages_spoken': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'English, French, Spanish...'}),
            'availability': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe when you are available to tutor...'}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Why do you want to volunteer as a tutor?'}),
            'commitment_level': forms.Select(attrs={'class': 'form-select'}),
            'volunteer_hours_goal': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100', 'placeholder': '10'}),
            'prefers_online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prefers_in_person': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'travel_distance': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tutoring.models import Subject
        self.fields['subjects'].queryset = Subject.objects.all()