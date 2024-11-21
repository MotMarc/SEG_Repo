"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', views.home, name='home'),  # Home screen
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard route
    path('log_in/', views.LogInView.as_view(), name='log_in'),  # Login route
    path('log_out/', views.log_out, name='log_out'),  # Logout route
    path('password/', views.PasswordView.as_view(), name='password'),  # Password change
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),  # Profile update
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),  # Signup route
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
