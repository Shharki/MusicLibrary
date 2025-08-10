from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LogoutView, LoginView,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import SignUpForm


class SignUpView(CreateView):
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    extra_context = {
        'title': 'Sign Up',
        'button_label': 'Register',
    }


class MyLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        logout(request)
        next_page = request.META.get('HTTP_REFERER') or '/'
        return redirect(next_page)


class MyLoginView(LoginView):
    template_name = 'form.html'
    authentication_form = AuthenticationForm
    extra_context = {
        'title': 'Login',
        'button_label': 'Log in',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.authentication_form(self.request)
        return context


# Not implemented yet
class MyPasswordChangeView(PasswordChangeView):
    template_name = 'form.html'
    extra_context = {
        'title': 'Change Password',
        'button_label': 'Change Password',
    }


# Not implemented yet
class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'form.html'
    extra_context = {
        'title': 'Password Changed',
        'done_message': 'Your password has been changed successfully.',
    }


class MyPasswordResetView(PasswordResetView):
    template_name = 'form.html'
    email_template_name = 'registration/password_reset_email.html'
    extra_context = {
        'title': 'Reset Password',
        'button_label': 'Send Reset Email',
    }


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'form.html'
    extra_context = {
        'title': 'Password Reset Sent',
        'done_message': (
            "Password reset sent.<br>"
            "We’ve emailed you instructions for setting your password, if an account exists with the email you entered. "
            "You should receive them shortly.<br><br>"
            "If you don’t receive an email, please make sure you’ve entered the address you registered with, and check your spam folder."
        ),
    }


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'form.html'
    extra_context = {
        'title': 'Set New Password',
        'button_label': 'Set Password',
    }


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'form.html'
    extra_context = {
        'title': 'Password Reset Complete',
        'done_message': 'Your password has been set. You may go ahead and log in now.',
    }
