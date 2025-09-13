import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")

from django.core.asgi import get_asgi_application
from tortoise import Tortoise
from test_project.tortoise_config import TORTOISE_ORM

django_app = get_asgi_application()

async def _init_orm():
    # IMPORTANT: we DO NOT generate schemas; we only connect to existing tables
    await Tortoise.init(config=TORTOISE_ORM)

async def _close_orm():
    await Tortoise.close_connections()

class TortoiseLifespan:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                msg = await receive()
                if msg["type"] == "lifespan.startup":
                    await _init_orm()
                    await send({"type": "lifespan.startup.complete"})
                elif msg["type"] == "lifespan.shutdown":
                    await _close_orm()
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        else:
            await self.app(scope, receive, send)

application = TortoiseLifespan(django_app)
