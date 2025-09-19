from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),  # Own profile
    path('profile/<int:user_id>/', views.profile_view, name='view_profile'),  # View other's profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]