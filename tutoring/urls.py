from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.tutor_search, name='tutor_search'),
    path('tutor/<int:tutor_id>/', views.tutor_detail, name='tutor_detail'),
    path('book/<int:tutor_id>/', views.book_session, name='book_session'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),  # Add this
    path('session/<int:session_id>/<str:action>/', views.session_action, name='session_action'),  # Add this
    path('complete-session/<int:session_id>/', views.complete_session, name='complete_session'),
    path('check-completion/<int:session_id>/', views.check_completion_status, name='check_completion_status'),
    path('review/<int:session_id>/', views.submit_review, name='submit_review'),
]