import asyncio
from typing import Type, Optional, Dict, Any, List
from django.db import models
from django.conf import settings
from tortoise import Tortoise, fields
from tortoise.models import Model as TortoiseModel

class RaphaelManager:
    """Async manager for Django models"""

    _initialized = False
    _init_lock = asyncio.Lock()
    _tortoise_models: Dict[str, Type[TortoiseModel]] = {}

    def __init__(self, django_model: Type[models.Model]):
        self.django_model = django_model
        self.tortoise_model = None

    async def _ensure_initialized(self):
        """Ensure Tortoise ORM is initialized"""
        if self._initialized:
            return

        async with self._init_lock:
            if self._initialized:
                return

            # Get Django database configuration
            db_config = settings.DATABASES.get('default', {})
            db_url = DjangoToTortoiseConverter.get_db_url(db_config)

            # Create all Tortoise models first
            tortoise_models = {}

            # Get the model for this manager
            model_key = f"{self.django_model._meta.app_label}.{self.django_model._meta.model_name}"
            if model_key not in self._tortoise_models:
                self.tortoise_model = TortoiseModelFactory.create_model(self.django_model)
                self._tortoise_models[model_key] = self.tortoise_model
                tortoise_models[self.tortoise_model.__name__] = self.tortoise_model
            else:
                self.tortoise_model = self._tortoise_models[model_key]
                tortoise_models[self.tortoise_model.__name__] = self.tortoise_model

            # Initialize Tortoise with the models
            await Tortoise.init(
                db_url=db_url,
                modules={'models': list(tortoise_models.values())},
                use_tz=getattr(settings, 'USE_TZ', True),
                timezone=str(getattr(settings, 'TIME_ZONE', 'UTC'))
            )

            # Generate schemas
            await Tortoise.generate_schemas(safe=True)

            RaphaelManager._initialized = True

    def _to_django(self, tortoise_obj):
        """Convert Tortoise object to Django model instance"""
        if tortoise_obj is None:
            return None

        kwargs = {}
        for field in self.django_model._meta.fields:
            if hasattr(tortoise_obj, field.name):
                value = getattr(tortoise_obj, field.name)
                kwargs[field.name] = value

        return self.django_model(**kwargs)

    def _to_django_list(self, tortoise_objs):
        """Convert list of Tortoise objects to Django model instances"""
        return [self._to_django(obj) for obj in tortoise_objs]

    async def all(self):
        """Get all objects"""
        await self._ensure_initialized()
        results = await self.tortoise_model.all()
        return self._to_django_list(results)

    async def filter(self, **kwargs):
        """Filter objects"""
        await self._ensure_initialized()
        results = await self.tortoise_model.filter(**kwargs)
        return self._to_django_list(results)

    async def exclude(self, **kwargs):
        """Exclude objects"""
        await self._ensure_initialized()
        results = await self.tortoise_model.exclude(**kwargs)
        return self._to_django_list(results)

    async def get(self, **kwargs):
        """Get a single object"""
        await self._ensure_initialized()
        result = await self.tortoise_model.get(**kwargs)
        return self._to_django(result)

    async def get_or_none(self, **kwargs):
        """Get a single object or None"""
        await self._ensure_initialized()
        result = await self.tortoise_model.get_or_none(**kwargs)
        return self._to_django(result)

    async def create(self, **kwargs):
        """Create a new object"""
        await self._ensure_initialized()
        result = await self.tortoise_model.create(**kwargs)
        return self._to_django(result)

    async def get_or_create(self, defaults=None, **kwargs):
        """Get or create an object"""
        await self._ensure_initialized()
        result, created = await self.tortoise_model.get_or_create(
            defaults=defaults, **kwargs
        )
        return self._to_django(result), created

    async def update_or_create(self, defaults=None, **kwargs):
        """Update or create an object"""
        await self._ensure_initialized()
        result, created = await self.tortoise_model.update_or_create(
            defaults=defaults, **kwargs
        )
        return self._to_django(result), created

    async def bulk_create(self, objects, batch_size=None):
        """Bulk create objects"""
        await self._ensure_initialized()

        # Convert Django objects to Tortoise objects
        tortoise_objs = []
        for obj in objects:
            data = {}
            for field in self.django_model._meta.fields:
                if hasattr(obj, field.name) and not field.primary_key:
                    value = getattr(obj, field.name)
                    if value is not None:
                        data[field.name] = value
            tortoise_objs.append(self.tortoise_model(**data))

        # Bulk create
        if batch_size:
            created = []
            for i in range(0, len(tortoise_objs), batch_size):
                batch = tortoise_objs[i:i + batch_size]
                batch_created = await self.tortoise_model.bulk_create(batch)
                created.extend(batch_created)
        else:
            created = await self.tortoise_model.bulk_create(tortoise_objs)

        return self._to_django_list(created)

    async def bulk_update(self, objects, fields, batch_size=None):
        """Bulk update objects"""
        await self._ensure_initialized()

        # Convert to Tortoise format and update
        for obj in objects:
            update_data = {}
            for field_name in fields:
                if hasattr(obj, field_name):
                    update_data[field_name] = getattr(obj, field_name)

            if obj.pk:
                await self.tortoise_model.filter(pk=obj.pk).update(**update_data)

        return len(objects)

    async def count(self):
        """Count all objects"""
        await self._ensure_initialized()
        return await self.tortoise_model.all().count()

    async def exists(self, **kwargs):
        """Check if objects exist"""
        await self._ensure_initialized()
        if kwargs:
            return await self.tortoise_model.filter(**kwargs).exists()
        return await self.tortoise_model.all().exists()

    async def aggregate(self, **kwargs):
        """Aggregate functions"""
        await self._ensure_initialized()
        return await self.tortoise_model.all().aggregate(**kwargs)

    async def first(self):
        """Get first object"""
        await self._ensure_initialized()
        result = await self.tortoise_model.all().first()
        return self._to_django(result)

    async def last(self):
        """Get last object"""
        await self._ensure_initialized()
        result = await self.tortoise_model.all().order_by('-id').first()
        return self._to_django(result)

    async def earliest(self, field_name):
        """Get earliest object by field"""
        await self._ensure_initialized()
        result = await self.tortoise_model.all().order_by(field_name).first()
        return self._to_django(result)

    async def latest(self, field_name):
        """Get latest object by field"""
        await self._ensure_initialized()
        result = await self.tortoise_model.all().order_by(f'-{field_name}').first()
        return self._to_django(result)

    async def in_bulk(self, id_list=None, field_name='pk'):
        """Get objects in bulk by IDs"""
        await self._ensure_initialized()

        if id_list:
            filter_kwargs = {f'{field_name}__in': id_list}
            results = await self.tortoise_model.filter(**filter_kwargs)
        else:
            results = await self.tortoise_model.all()

        # Return dict mapping field values to objects
        return {
            getattr(obj, field_name): self._to_django(obj)
            for obj in results
        }

    async def delete(self):
        """Delete all objects"""
        await self._ensure_initialized()
        return await self.tortoise_model.all().delete()

    async def update(self, **kwargs):
        """Update all objects"""
        await self._ensure_initialized()
        return await self.tortoise_model.all().update(**kwargs)

    def order_by(self, *fields):
        """Return a QuerySet ordered by fields"""
        return RaphaelQuerySet(self, self.tortoise_model.all().order_by(*fields))

    def values(self, *fields):
        """Return a QuerySet that returns dictionaries"""
        return RaphaelQuerySet(self, self.tortoise_model.all().values(*fields))

    def values_list(self, *fields, flat=False):
        """Return a QuerySet that returns tuples"""
        return RaphaelQuerySet(self, self.tortoise_model.all().values_list(*fields, flat=flat))


class RaphaelQuerySet:
    """Async QuerySet wrapper for chaining operations"""

    def __init__(self, manager, queryset):
        self.manager = manager
        self.queryset = queryset

    def filter(self, **kwargs):
        """Filter the queryset"""
        self.queryset = self.queryset.filter(**kwargs)
        return self

    def exclude(self, **kwargs):
        """Exclude from the queryset"""
        self.queryset = self.queryset.exclude(**kwargs)
        return self

    def order_by(self, *fields):
        """Order the queryset"""
        self.queryset = self.queryset.order_by(*fields)
        return self

    def limit(self, n):
        """Limit the queryset"""
        self.queryset = self.queryset.limit(n)
        return self

    def offset(self, n):
        """Offset the queryset"""
        self.queryset = self.queryset.offset(n)
        return self

    async def all(self):
        """Execute and return all results"""
        await self.manager._ensure_initialized()
        results = await self.queryset
        return self.manager._to_django_list(results)

    async def first(self):
        """Get first result"""
        await self.manager._ensure_initialized()
        result = await self.queryset.first()
        return self.manager._to_django(result)

    async def last(self):
        """Get last result"""
        await self.manager._ensure_initialized()
        results = await self.queryset
        if results:
            return self.manager._to_django(results[-1])
        return None

    async def count(self):
        """Count results"""
        await self.manager._ensure_initialized()
        return await self.queryset.count()

    async def exists(self):
        """Check if results exist"""
        await self.manager._ensure_initialized()
        return await self.queryset.exists()

    async def delete(self):
        """Delete all matching objects"""
        await self.manager._ensure_initialized()
        return await self.queryset.delete()

    async def update(self, **kwargs):
        """Update all matching objects"""
        await self.manager._ensure_initialized()
        return await self.queryset.update(**kwargs)


class AsyncManagerDescriptor:
    """Descriptor to provide async manager access at the class level"""

    def __init__(self):
        self._managers = {}

    def __get__(self, obj, owner):
        if owner not in self._managers:
            self._managers[owner] = RaphaelManager(owner)
        return self._managers[owner]
