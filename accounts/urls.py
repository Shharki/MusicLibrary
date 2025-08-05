from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordChangeDoneView,
)
from django.urls import path

from accounts.views import MyLogoutView

urlpatterns = [
path('accounts/login/', LoginView.as_view(template_name='form.html'), name='login'),
# Custom Logout through Form with working HTTP_REFERER. Safer because of csrf token.
path('accounts/logout/', MyLogoutView.as_view(next_page='/'), name='logout'),

# Alternative logout
# Default Logout as Form, HTTP_REFERER doesn't work here
# path('accounts/logout/', LogoutView.as_view(), name='logout'),
# Logout through def from accounts/views.py
# path('accounts/logout/', user_logout, name='logout'),

path('password_change/',
     PasswordChangeView.as_view(template_name='form.html'), name='password_change'),
path('password_change/done/',
     PasswordChangeDoneView.as_view(template_name='form.html'), name='password_change_done'),
]