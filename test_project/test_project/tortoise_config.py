from django.conf import settings

DJ = settings.DATABASES["default"]

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": DJ.get("HOST", "localhost"),     # e.g. "db"
                "port": int(DJ.get("PORT", 5432)),       # e.g. 5432
                "user": DJ.get("USER", "postgres"),
                "password": DJ.get("PASSWORD", ""),
                "database": DJ.get("NAME", "postgres"),
                # Optional:
                # "schema": "public",
                # "minsize": 1, "maxsize": 10, "command_timeout": 60,
            },
        }
    },
    "apps": {
        "models": {
            "models": [
                "test_project.books.tortoise_models",  # where TortoiseBook lives
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",  # or match settings.TIME_ZONE
}
