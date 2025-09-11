import asyncio
from typing import Type, Optional, Dict, Any, List
from django.db import models
from django.conf import settings
from tortoise import Tortoise, fields
from tortoise.models import Model as TortoiseModel

from django_raphael.managers import AsyncManagerDescriptor


class TortoiseModelFactory:
    """Factory for creating Tortoise models from Django models"""

    _models: Dict[str, Type[TortoiseModel]] = {}

    @classmethod
    def create_model(cls, django_model: Type[models.Model]) -> Type[TortoiseModel]:
        """Create or get a Tortoise model that mirrors a Django model"""

        model_key = f"{django_model._meta.app_label}.{django_model._meta.model_name}"

        if model_key in cls._models:
            return cls._models[model_key]

        # Map Django fields to Tortoise fields
        attrs = {}

        for field in django_model._meta.fields:
            name = field.name

            # Primary key fields
            if field.primary_key:
                if isinstance(field, models.BigAutoField):
                    attrs[name] = fields.BigIntField(pk=True)
                elif isinstance(field, models.AutoField):
                    attrs[name] = fields.IntField(pk=True)
                elif isinstance(field, models.UUIDField):
                    attrs[name] = fields.UUIDField(pk=True)
                else:
                    attrs[name] = fields.IntField(pk=True)

            # String fields
            elif isinstance(field, models.CharField):
                attrs[name] = fields.CharField(
                    max_length=field.max_length,
                    null=field.null,
                    default=field.default if field.has_default() else None
                )
            elif isinstance(field, models.EmailField):
                attrs[name] = fields.CharField(
                    max_length=field.max_length or 254,
                    null=field.null
                )
            elif isinstance(field, models.URLField):
                attrs[name] = fields.CharField(
                    max_length=field.max_length or 200,
                    null=field.null
                )
            elif isinstance(field, models.TextField):
                attrs[name] = fields.TextField(null=field.null)

            # Numeric fields
            elif isinstance(field, models.IntegerField):
                attrs[name] = fields.IntField(
                    null=field.null,
                    default=field.default if field.has_default() else None
                )
            elif isinstance(field, models.BigIntegerField):
                attrs[name] = fields.BigIntField(null=field.null)
            elif isinstance(field, models.SmallIntegerField):
                attrs[name] = fields.SmallIntField(null=field.null)
            elif isinstance(field, models.FloatField):
                attrs[name] = fields.FloatField(null=field.null)
            elif isinstance(field, models.DecimalField):
                attrs[name] = fields.DecimalField(
                    max_digits=field.max_digits,
                    decimal_places=field.decimal_places,
                    null=field.null
                )

            # Boolean field
            elif isinstance(field, models.BooleanField):
                attrs[name] = fields.BooleanField(
                    default=field.default if field.has_default() else False,
                    null=field.null
                )

            # Date/time fields
            elif isinstance(field, models.DateTimeField):
                attrs[name] = fields.DatetimeField(
                    null=field.null,
                    auto_now=field.auto_now,
                    auto_now_add=field.auto_now_add
                )
            elif isinstance(field, models.DateField):
                attrs[name] = fields.DateField(
                    null=field.null,
                    auto_now=field.auto_now,
                    auto_now_add=field.auto_now_add
                )
            elif isinstance(field, models.TimeField):
                attrs[name] = fields.TimeField(null=field.null)

            # Other fields
            elif isinstance(field, models.UUIDField):
                attrs[name] = fields.UUIDField(null=field.null)
            elif isinstance(field, models.JSONField):
                attrs[name] = fields.JSONField(null=field.null)
            elif isinstance(field, models.BinaryField):
                attrs[name] = fields.BinaryField(null=field.null)

        # Create Meta class
        table_name = django_model._meta.db_table or \
                     f"{django_model._meta.app_label}_{django_model._meta.model_name}"

        class Meta:
            table = table_name

        attrs['Meta'] = Meta

        # Create the Tortoise model
        model_name = f"{django_model.__name__}Tortoise"
        tortoise_model = type(model_name, (TortoiseModel,), attrs)

        # Cache the model
        cls._models[model_key] = tortoise_model

        return tortoise_model


class RaphaelMixin:
    """
    Mixin for Django models to add async ORM capabilities via Tortoise ORM.
    Automatically uses Django's database configuration.

    Usage:
        class Book(RaphaelMixin, models.Model):
            title = models.CharField(max_length=200)
            author = models.CharField(max_length=100)

        # Async operations
        book = await Book.aobjects.get(id=245)
        books = await Book.aobjects.filter(author="John").all()
        new_book = await Book.aobjects.create(title="New", author="Author")
    """

    aobjects = AsyncManagerDescriptor()

    async def asave(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Async save method"""
        manager = self.__class__.aobjects
        await manager._ensure_initialized()

        # Prepare data
        data = {}
        fields_to_update = update_fields or [f.name for f in self._meta.fields]

        for field_name in fields_to_update:
            field = self._meta.get_field(field_name)
            if not field.primary_key:
                value = getattr(self, field_name)
                if value is not None:
                    data[field_name] = value

        if self.pk and not force_insert:
            # Update existing
            await manager.tortoise_model.filter(pk=self.pk).update(**data)
        else:
            # Create new
            obj = await manager.tortoise_model.create(**data)
            self.pk = obj.pk

        return self

    async def adelete(self, using=None, keep_parents=False):
        """Async delete method"""
        if self.pk:
            manager = self.__class__.aobjects
            await manager._ensure_initialized()
            await manager.tortoise_model.filter(pk=self.pk).delete()

    async def arefresh_from_db(self, using=None, fields=None):
        """Async refresh from database"""
        if self.pk:
            manager = self.__class__.aobjects
            await manager._ensure_initialized()
            obj = await manager.tortoise_model.get(pk=self.pk)

            fields_to_refresh = fields or [f.name for f in self._meta.fields]
            for field_name in fields_to_refresh:
                if hasattr(obj, field_name):
                    setattr(self, field_name, getattr(obj, field_name))
