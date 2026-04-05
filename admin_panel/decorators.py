from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('control_panel:login')
        if not request.user.is_staff:
            return redirect('control_panel:login')
        if not request.session.get('_admin_authenticated'):
            return redirect('control_panel:login')
        return view_func(request, *args, **kwargs)
    return wrapper
