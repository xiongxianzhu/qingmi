# coding: utf-8

from flask_admin.contrib.mongoengine.filters import (
    BaseMongoEngineFilter, FilterConverter as _FilterConverter,
)
from flask_admin.model import filters
from mongoengine.fields import (IntField, LongField, DecimalField,
                            FloatField, StringField)


class FilterConverter(_FilterConverter):

    # def convert(self, type_name, column, name):
    #     filter_name = type_name.lower()

    #     if filter_name in self.converters:
    #         return self.converters[filter_name](column, name)

    #     return None
    
    @filters.convert('DynamicField')
    def conv_dynamic(self, column, name):
        dynamic_filters = self.strings
        # data_type = self.get_data_type(column)
        # if data_type == int:
        #     dynamic_filters = self.int_filters
        # elif data_type == float:
        #     dynamic_filters = self.float_filters
        # elif data_type == str:
        #     dynamic_filters = self.strings
        # elif data_type == bool:
        #     dynamic_filters = self.bool_filter
        return [f(column, name) for f in dynamic_filters]


    def get_data_type(self, column):
        data_type = None
        if isinstance(column, IntField) or isinstance(column, LongField):
            data_type = int
        elif isinstance(column, DecimalField) or isinstance(column, FloatField):
            data_type = float
        elif isinstance(column, StringField):
            data_type = str
        return data_type


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


BaseMongoEngineFilter.get_options = get_options
