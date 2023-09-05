"""
ASGI config for django_ws project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_ws.settings')

# application = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from api.consumers import TokenAuthConsumer
from api.middlewares import TokenAuthMiddleWare

print("This is in ASGIIIIIIIIIIIIIIIIIIIII")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": TokenAuthMiddleWare(
			AllowedHostsOriginValidator(
				URLRouter(
				[path("", TokenAuthConsumer.as_asgi())]
				)
			)
		),
    }
)
