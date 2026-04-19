from functools import wraps

from django.shortcuts import redirect

from .models import Supervisor


def supervisor_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        supervisor_id = request.session.get("supervisor_id")
        if not supervisor_id:
            return redirect("accounts:login")

        exists = Supervisor.objects.filter(id=supervisor_id, is_active=True).exists()
        if not exists:
            request.session.flush()
            return redirect("accounts:login")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def get_current_supervisor(request):
    supervisor_id = request.session.get("supervisor_id")
    return Supervisor.objects.filter(id=supervisor_id, is_active=True).first()