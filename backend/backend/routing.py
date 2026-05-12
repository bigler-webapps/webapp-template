# backend/routing.py
#
# ASGI/Channels routing. Default: HTTP only, no WebSocket routes registered.
# When your app needs WebSocket support, import its routing module and add
# its url_patterns to the websocket URLRouter below.
#
# Example:
#     import myapp.routing
#     URLRouter(myapp.routing.websocket_urlpatterns)

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter([]),
    }
)
