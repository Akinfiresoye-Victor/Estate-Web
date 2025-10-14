#this handles the websocket url patterns 

from django.urls import path
from .consumer import ChatConsumer

#url routing for our websocket routing
websocket_urlpatterns = [
    path('ws/community/<str:room_name>/', ChatConsumer.as_asgi()),
]