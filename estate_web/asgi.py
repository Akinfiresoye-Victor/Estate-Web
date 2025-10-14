"""An ASGI application is used when working with WebSockets"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # ← this line is crucial
from estate import routing

# Set up the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estate_web.settings')

# Initialize the Django ASGI application
django_asgi_app = get_asgi_application()

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(      # ← wrap your router with AuthMiddlewareStack
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
