from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))


class MyLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        logout(request)  # explicitní logout
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or '/')


def path(request):
    return None