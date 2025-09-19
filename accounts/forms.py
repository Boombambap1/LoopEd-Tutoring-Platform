from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    birth_month = forms.ChoiceField(
        choices=[
            ('', 'Select Month'),
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    birth_day = forms.ChoiceField(
        choices=[('', 'Select Day')] + [(i, i) for i in range(1, 32)],  # Keep all days 1-31
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    birth_year = forms.ChoiceField(
        choices=[('', 'Select Year')] + [(i, i) for i in range(2013, 1920, -1)],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_month', 'birth_day', 'birth_year', 'user_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        birth_month = cleaned_data.get('birth_month')
        birth_day = cleaned_data.get('birth_day')
        birth_year = cleaned_data.get('birth_year')
        
        
        
        if birth_month and birth_day and birth_year:
            try:
                # Create the birthday date - this will automatically validate impossible dates
                birthday = date(int(birth_year), int(birth_month), int(birth_day))
                
                # Validate age
                today = date.today()
                age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
                
                if age < 13:
                    raise forms.ValidationError("You must be at least 13 years old to register.")
                if age > 100:
                    raise forms.ValidationError("Please enter a valid birth date.")
                
                # Store the combined birthday for saving
                cleaned_data['birthday'] = birthday
                
            except ValueError as e:
                # This will catch invalid dates like Feb 31st
                if "day is out of range for month" in str(e):
                    raise forms.ValidationError(f"Invalid date: {birth_month}/{birth_day}/{birth_year}. Please check the day for the selected month.")
                else:
                    raise forms.ValidationError("Invalid date. Please check your birth date.")
        else:
            raise forms.ValidationError("Please select your complete birth date (month, day, and year).")
            
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the birthday from our combined date
        if hasattr(self, 'cleaned_data') and 'birthday' in self.cleaned_data:
            user.birthday = self.cleaned_data['birthday']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )