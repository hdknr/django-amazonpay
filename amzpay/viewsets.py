from rest_framework import (viewsets, response)
from social_django.utils import load_strategy, load_backend
from social_django.views import _do_login


class TokenViewSet(viewsets.ViewSet):

    def auth(self, request):
        backend = load_backend(load_strategy(request), 'amazon', '')
        user = user if request.user.is_authenticated else None
        res = backend.do_auth(
            request.data.get('access_token', ''),
            response=request.data, user=user, request=request)
        _do_login(backend, res, getattr(res, 'social_user', None))
        return res

    def create(self, request):
        user = self.auth(request)
        return response.Response(dict(username=user and user.username))
