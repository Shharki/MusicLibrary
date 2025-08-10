from django.urls import path, include
from accounts.views import (
    MyLogoutView, SignUpView, MyLoginView,
    MyPasswordChangeView, MyPasswordChangeDoneView,
    MyPasswordResetView, MyPasswordResetDoneView,
    MyPasswordResetConfirmView, MyPasswordResetCompleteView,
)

urlpatterns = [
    path('login/', MyLoginView.as_view(template_name="form.html"), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),

    path('password_change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', MyPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    # Not implemented yet
    path('reset/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Not implemented yet
    path('reset/done/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('signup/', SignUpView.as_view(template_name='form.html'), name='signup'),
    # path('', include('django.contrib.auth.urls')),
]
