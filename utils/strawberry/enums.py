import typing
import strawberry

from django.db import models
from django.db.models.fields import Field as DjangoBaseField
from django.utils.hashable import make_hashable
from django.utils.encoding import force_str
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers

from utils.common import to_camel_case


def get_enum_name_from_django_field(
    field: None | DjangoBaseField,
    field_name=None,
    model_name=None,
    serializer_name=None,
):
    def _have_model(_field):
        if hasattr(_field, 'model') or hasattr(getattr(_field, 'Meta', None), 'model'):
            return True

    def _get_serializer_name(_field):
        if hasattr(_field, 'parent'):
            return type(_field.parent).__name__

    if field_name is None or model_name is None:
        if isinstance(field, models.query_utils.DeferredAttribute):
            return get_enum_name_from_django_field(
                field.field,
                field_name=field_name,
                model_name=model_name,
                serializer_name=serializer_name,
            )
        if isinstance(field, serializers.ChoiceField):
            if isinstance(field.parent, serializers.ListField):
                if _have_model(field.parent.parent):
                    model_name = model_name or field.parent.parent.Meta.model.__name__
                serializer_name = _get_serializer_name(field.parent)
                field_name = field_name or field.parent.field_name
            else:
                if _have_model(field.parent):
                    model_name = model_name or field.parent.Meta.model.__name__
                serializer_name = _get_serializer_name(field)
                field_name = field_name or field.field_name
        elif isinstance(field, ArrayField):
            if _have_model(field):
                model_name = model_name or field.model.__name__
            serializer_name = _get_serializer_name(field)
            field_name = field_name or field.base_field.name
        elif isinstance(field, (
            models.CharField,
            models.SmallIntegerField,
            models.IntegerField,
            models.PositiveSmallIntegerField,
        )):
            if _have_model(field):
                model_name = model_name or field.model.__name__
            serializer_name = _get_serializer_name(field)
            field_name = field_name or field.name
    if field_name is None:
        raise Exception(f'{field=} should have a name')
    if model_name:
        return f'{model_name}{to_camel_case(field_name.title())}'
    if serializer_name:
        return f'{serializer_name}{to_camel_case(field_name.title())}'
    raise Exception(f'{serializer_name=} should have a value')


def enum_display_field(field) -> typing.Callable[..., str]:
    field: DjangoBaseField
    _field = field
    if isinstance(field, models.query_utils.DeferredAttribute):
        _field = field.field

    if is_array := isinstance(_field, ArrayField):
        _field = _field.base_field

    def _get_value(root) -> None | str | list[str]:
        # https://github.com/django/django/blob/stable/4.2.x/django/db/models/base.py#L1144-L1150
        value = getattr(root, _field.attname)
        if value is None:
            return
        choices_dict = dict(make_hashable(_field.flatchoices))
        # force_str() to coerce lazy strings.
        if is_array:
            return [
                force_str(
                    choices_dict.get(make_hashable(v), v), strings_only=True
                )
                for v in value or []
            ]
        return force_str(
            choices_dict.get(make_hashable(value), value), strings_only=True
        )

    @strawberry.field
    def array_field_(root) -> list[str]:
        return _get_value(root)

    if is_array:
        return array_field_

    @strawberry.field
    def field_(root) -> str:
        return _get_value(root)

    @strawberry.field
    def nullable_field_(root) -> typing.Optional[str]:
        return _get_value(root)

    if _field.null:
        return nullable_field_
    return field_


def enum_field(field):
    field: DjangoBaseField

    # NOTE: To avoid circular import
    from main.enums import ENUM_TO_STRAWBERRY_ENUM_MAP

    _field = field
    if isinstance(field, models.query_utils.DeferredAttribute):
        _field = field.field
    FieldEnum = ENUM_TO_STRAWBERRY_ENUM_MAP[get_enum_name_from_django_field(field)]

    if is_array := isinstance(_field, ArrayField):
        _field = _field.base_field

    def _get_value(root) -> None | FieldEnum | list[FieldEnum]:
        value = getattr(root, _field.attname)
        if value is None:
            return
        if is_array:
            return [
                FieldEnum(v) for v in value or []
            ]
        return FieldEnum(value)

    @strawberry.field
    def array_field_(root) -> list[FieldEnum]:
        return _get_value(root)

    if is_array:
        return array_field_

    @strawberry.field
    def field_(root) -> FieldEnum:
        return _get_value(root)

    @strawberry.field
    def nullable_field_(root) -> typing.Optional[FieldEnum]:
        return _get_value(root)

    if _field.null:
        return nullable_field_
    return field_
