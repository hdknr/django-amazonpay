from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import viewsets

router = DefaultRouter()
router.register(r'token', viewsets.TokenViewSet, base_name='token')
router.register(r'payorder', viewsets.PayOrderViewSet, base_name='payorder')


urlpatterns = [
    url(r'^', include(router.urls)),
]
