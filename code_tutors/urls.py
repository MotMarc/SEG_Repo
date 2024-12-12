from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views  # Ensure 'tutorials' is your app name
from tutorials.views import calendar_bookings_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),

    # Booking URL paths
    path('create-booking/', views.create_booking, name='create_booking'),
    path('bookings/view/', views.view_bookings, name='view_bookings'),  # Ensure this line exists

    # Admin-specific Booking Management URLs
    path('bookings/admin/pending/', views.pending_bookings, name='admin_pending_bookings'),
    path('bookings/admin/pending/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('bookings/admin/pending/decline/<int:booking_id>/', views.decline_booking, name='decline_booking'),
    path('bookings/admin/create/', views.admin_create_booking, name='admin_create_booking'),
    path('bookings/admin/create/', views.admin_create_booking, name='admin_create_booking'),

    # Removed duplicate URL pattern below to avoid conflicts
    # path('admin/bookings/create/', views.admin_create_booking, name='admin_create_booking'),

    # Tutor Profile
    path('tutor/profile/', views.tutor_profile, name='tutor_profile'),

    # User Booking Actions
    path('bookings/accept/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('bookings/reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    
    path('api/calendar/', views.booking_calendar_data, name='booking_calendar_data'),
    path('api/calendar-bookings/', views.calendar_bookings_api, name='calendar_bookings_api'),

    #...
    path('tutor/profile/availability/', views.tutor_availability, name='tutor_availability'),


]

# Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers (ensure these views exist in tutorials/views.py)
handler404 = 'tutorials.views.custom_404_view'
handler500 = 'tutorials.views.custom_500_view'