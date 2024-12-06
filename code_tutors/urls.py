from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, reverse_lazy
from tutorials import views
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Landing page
    path('dashboard/', views.dashboard, name='dashboard'),  # Shared dashboard redirect
    path('log_in/', views.LogInView.as_view(), name='log_in'),  # Log in
    path('log_out/', views.log_out, name='log_out'),  # Log out
    path('password/', views.PasswordView.as_view(), name='password'),  # Password reset or change
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),  # Update profile
    path('profile/change-password/',
         PasswordChangeView.as_view(
             template_name='change_password.html',
             success_url=reverse_lazy('profile')  # Redirect to the profile page after success
         ),
         name='change_password'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),  # Sign-up page

    # Student-specific dashboard and actions
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/request-meeting/', views.request_booking, name='request_meeting'),  # Request meeting
    path('dashboard/student/view-meetings/', views.view_bookings, name='view_meetings'),

    # Tutor-specific dashboard and actions
    path('dashboard/tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('dashboard/tutor/change-language/', views.change_language, name='change_language'),
    path('dashboard/tutor/view-bookings/', views.view_tutor_bookings, name='view_bookings'),  # View tutor bookings
]

# Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
