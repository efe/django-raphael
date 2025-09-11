from typing import Dict, Any

from tortoise import Tortoise


class DjangoToTortoiseConverter:
    """Converts Django database configuration to Tortoise ORM format"""

    @staticmethod
    def get_db_url(db_config: Dict[str, Any]) -> str:
        """Convert Django database configuration to Tortoise ORM URL"""
        engine = db_config.get('ENGINE', '')

        # SQLite
        if 'sqlite' in engine:
            name = db_config.get('NAME', 'db.sqlite3')
            if name == ':memory:':
                return 'sqlite://:memory:'
            return f'sqlite://{name}'

        # PostgreSQL
        if 'postgresql' in engine or 'psycopg' in engine:
            scheme = 'postgres'
        # MySQL
        elif 'mysql' in engine:
            scheme = 'mysql'
        else:
            raise ValueError(f"Unsupported database engine: {engine}")

        # Build connection URL
        user = db_config.get('USER', '')
        password = db_config.get('PASSWORD', '')
        host = db_config.get('HOST', 'localhost')
        port = db_config.get('PORT', '')
        name = db_config.get('NAME', '')

        url = f"{scheme}://"
        if user:
            url += user
            if password:
                url += f":{password}"
            url += "@"
        url += host
        if port:
            url += f":{port}"
        url += f"/{name}"

        return url


async def close_connections():
    """Close all Tortoise ORM connections"""
    await Tortoise.close_connections()
