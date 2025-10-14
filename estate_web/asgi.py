'''An asgi application is used when working with web sockets'''
import os

# imports
#the protocoltyperouter routes incommingconnections based on http,websockets etc.., The URLRouter works like django urls to the view it tells websocket which consumer it should use based on the url
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from estate import routing

# this is used to set up the django settings model if it hasnt been setup already this should come before initializing the asgi application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estate_web.settings')

#setting our django instance up it must be called after we already set our default environment
django_asgi_app = get_asgi_application()



application = ProtocolTypeRouter({
    #routes all http methods to our django_asgi_app
    "http": django_asgi_app,
    #routes all our websocket connection
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    )
})