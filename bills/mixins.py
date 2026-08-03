from functools import wraps

from django.shortcuts import redirect


def require_organisation(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'membership'):
            return redirect('setup')
        request.organization = request.user.membership.organization
        return view_func(request, *args, **kwargs)

    return wrapper
