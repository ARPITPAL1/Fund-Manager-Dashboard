from django.urls import re_path, path
from .consumers import TransactionLiveConsumer

websocket_urlpatterns = [
    re_path(r'^ws/?$', TransactionLiveConsumer.as_asgi()),
    path('ws', TransactionLiveConsumer.as_asgi()),
]
