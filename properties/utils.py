from functools import wraps
from django.http import HttpResponseForbidden

def landlord_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'landlord'):  # Verifica se o usuário é Landlord
            return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
