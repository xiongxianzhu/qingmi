# coding: utf-8

from flask_admin.contrib.mongoengine.filters import (
    BaseMongoEngineFilter, FilterConverter as _FilterConverter,
    FilterEqual, FilterNotEqual, FilterLike, FilterNotLike
)
from flask_admin.model import filters
from mongoengine.fields import (IntField, LongField, DecimalField,
                            FloatField, StringField, ObjectIdField,
                            ReferenceField, DynamicField)
from bson.objectid import ObjectId
from flask_admin.babel import lazy_gettext


# def get_value_type(column):
#     print('get_value_type====', dir(column))
#     document, value_type = column._owner_document, None
#     if hasattr(document, 'id'):
#         attr = document._fields.get('id')
#         if isinstance(attr, IntField) or isinstance(attr, LongField):
#             value_type = int
#         elif isinstance(attr, DecimalField) or isinstance(attr, FloatField):
#             value_type = float
#         elif isinstance(attr, ObjectIdField):
#             value_type = ObjectId
#     return value_type


def get_value_type(column):
    value_type = None
    if isinstance(column, IntField) or isinstance(column, LongField):
        value_type = int
    elif isinstance(column, DecimalField) or isinstance(column, FloatField):
        value_type = float
    elif isinstance(column, ObjectIdField):
        value_type = ObjectId
    elif isinstance(column, StringField):
        value_type = str
    elif isinstance(column, ReferenceField):
        document_type = column.document_type
        if hasattr(document_type, 'id'):
            attr = document_type._fields.get('id')
            if isinstance(attr, IntField) or isinstance(attr, LongField):
                value_type = int
            elif isinstance(attr, DecimalField) or isinstance(attr, FloatField):
                value_type = float
            elif isinstance(attr, ObjectIdField):
                value_type = ObjectId
            elif isinstance(attr, StringField):
                value_type = str
    elif isinstance(column, DynamicField):
        pass
    return value_type


class BaseReferenceFilter(BaseMongoEngineFilter):

    def __init__(self, column, name, options=None, data_type=None):
        super(BaseReferenceFilter, self).__init__(column, name, options, data_type)
        self.value_type = get_value_type(column)
    
    def validate(self, value):
        """
            Validate value.
            If value is valid, returns `True` and `False` otherwise.
            :param value:
                Value to validate
        """
        try:
            self.clean(value)
            return True
        except InvalidId:
            return False

    def clean(self, value):
        if self.value_type == int:
            return int(value.strip())
        elif self.value_type == float:
            return float(value)
        elif self.value_type == ObjectId:
            if len(str(value)) != 24:
                return '0'*24
        return value


class ReferenceFilterEqual(FilterEqual, BaseReferenceFilter):
    pass


class ReferenceFilterNotEqual(FilterNotEqual, BaseReferenceFilter):
    pass


class BaseObjectIdFilter(BaseMongoEngineFilter):

    def __init__(self, column, name, options=None, data_type=None):
        super(BaseObjectIdFilter, self).__init__(column, name, options, data_type)
        self.value_type = get_value_type(column)

    def validate(self, value):
        try:
            self.clean(value)
            return True
        except InvalidId:
            return False

    def clean(self, value):
        if self.value_type == int:
            return int(float(value))
        elif self.value_type == float:
            return float(value)
        elif self.value_type == ObjectId:
            if len(str(value)) != 24:
                return '0'*24
        return value


class ObjectIdFilterEqual(FilterEqual, BaseObjectIdFilter):
    pass


class ObjectIdFilterNotEqual(FilterNotEqual, BaseObjectIdFilter):
    pass


class BaseDynamicFilter(BaseMongoEngineFilter):

    def __init__(self, column, name, options=None, data_type=None):
        super(BaseDynamicFilter, self).__init__(column, name, options, data_type)
        self.value_type = get_value_type(column)

    def clean(self, value):
        return value


class DynamicEqualFilter(FilterEqual, BaseDynamicFilter):
    pass


class DynamicNotEqualFilter(FilterNotEqual, BaseDynamicFilter):
    pass


class DynamicLikeFilter(FilterLike, BaseDynamicFilter):
    pass


class DynamicNotLikeFilter(FilterNotLike, BaseDynamicFilter):
    pass



class FilterConverter(_FilterConverter):

    reference_filters = (ReferenceFilterEqual, ReferenceFilterNotEqual)
    object_id_filters = (ObjectIdFilterEqual, ObjectIdFilterNotEqual)
    dynamic_filters = (DynamicEqualFilter, DynamicNotEqualFilter,
                        DynamicLikeFilter, DynamicNotLikeFilter)

    def convert(self, type_name, column, name):
        filter_name = type_name.lower()

        if filter_name in self.converters:
            return self.converters[filter_name](column, name)
        return None
    
    @filters.convert('DynamicField')
    def conv_dynamic(self, column, name):
        return [f(column, name) for f in self.dynamic_filters]

    @filters.convert('ReferenceField')
    def conv_reference(self, column, name):
        return [f(column, name) for f in self.reference_filters]

    @filters.convert('ObjectIdField')
    def conv_object_id(self, column, name):
        return [f(column, name) for f in self.object_id_filters]



def get_options(self, view):
    """
        Return list of predefined options.

        Override to customize behavior.

        :param view:
            Associated administrative view class.
    """
    options = self.options or self.column.choices

    if options:
        if callable(options):
            options = options()

        return options

    return None


# BaseMongoEngineFilter.get_options = get_options
