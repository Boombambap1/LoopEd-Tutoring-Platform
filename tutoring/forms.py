from django import forms
from .models import Subject, TutoringSession
from datetime import date, datetime

class TutorSearchForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter location',
            'class': 'form-control'
        })
    )
    max_rate = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max hourly rate',
            'class': 'form-control'
        })
    )

class BookingForm(forms.Form):  # Add this new form
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),  # Will be set dynamically
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    duration_hours = forms.ChoiceField(
        choices=[
            ('1.0', '1 hour'),
            ('1.5', '1.5 hours'),
            ('2.0', '2 hours'),
            ('2.5', '2.5 hours'),
            ('3.0', '3 hours'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    preferred_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().strftime('%Y-%m-%d')  # Can't book in the past
        })
    )
    preferred_time = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tell the tutor about your learning goals, specific topics you\'d like to cover, or any other relevant information...'
        })
    )
    
    def __init__(self, tutor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the subject choices to only the tutor's subjects
        self.fields['subject'].queryset = tutor.subjects.all()
        
    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        preferred_time = cleaned_data.get('preferred_time')
        
        if preferred_date and preferred_time:
            # Combine date and time
            session_datetime = datetime.combine(preferred_date, preferred_time)
            
            # Check if it's in the past
            if session_datetime < datetime.now():
                raise forms.ValidationError("You cannot book a session in the past.")
                
        return cleaned_data