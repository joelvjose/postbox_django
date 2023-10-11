
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django_asgi_application = get_asgi_application()

from chat import routing as chatrouting
from post import routing as postrouting

application = ProtocolTypeRouter(
    {
        "http":django_asgi_application,
        "websocket":
            AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(
                URLRouter(chatrouting.websocket_urlpatterns + postrouting.websocket_urlpatterns)
                )
        )
    }
)
