import functools
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def ratelimit(rate='30/m', methods=('POST',), key_prefix=None):
    """
    Drop-in rate limiting decorator. Uses Django's cache backend.
    Fails open (allows request) if cache is unavailable.
    Returns JSON for AJAX requests, HTML for normal requests.

    Usage:
        @ratelimit(rate='30/m', methods=('POST',))
        def my_view(request):
            ...
    """
    count_str, period_str = rate.split('/')
    max_requests = int(count_str)
    period_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    window_seconds = period_map[period_str.lower()]

    def decorator(view_func):
        prefix = key_prefix or view_func.__name__

        @functools.wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.method.upper() in [m.upper() for m in methods]:
                ip = _get_client_ip(request)
                cache_key = f"rl:{prefix}:{ip}"

                try:
                    count = cache.get(cache_key)
                    if count is None:
                        cache.set(cache_key, 1, window_seconds)
                    elif count >= max_requests:
                        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                        if is_ajax:
                            return JsonResponse(
                                {'error': 'Too many requests. Please wait a moment.'},
                                status=429
                            )
                        return render(request, 'core/429.html', status=429)
                    else:
                        cache.incr(cache_key)
                except Exception:
                    pass  # cache unavailable — fail open, allow the request

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator