from django.http import HttpResponse


class RailwayHealthcheckMiddleware:
    """Answer Railway's internal probe before Django validates its private host."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info == "/healthz/":
            return HttpResponse("ok", content_type="text/plain")

        return self.get_response(request)
