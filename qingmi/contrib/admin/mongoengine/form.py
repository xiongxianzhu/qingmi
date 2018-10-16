# coding: utf-8
from flask_mongoengine.wtf import orm
from flask_admin import form
from flask_admin.contrib.mongoengine.form import (CustomModelConverter 
            as _CustomModelConverter)
from flask_admin.model.fields import AjaxSelectField
from wtforms import fields as f
from qingmi.form.fields import XFileField, XImageField


class CustomModelConverter(_CustomModelConverter):
    """
        Customized MongoEngine form conversion class.

        Injects various Flask-Admin widgets and handles lists with
        customized InlineFieldList field.
    """

    @orm.converts('DynamicField')
    def conv_dynamic(self, model, field, kwargs):
        textarea_field = kwargs.pop('textarea', True)
        if textarea_field:
            return f.TextAreaField(**kwargs)
        return f.StringField(**kwargs)

    @orm.converts('XFileField')
    def conv_xfile(self, model, field, kwargs):
        return XFileField(max_size=field.max_size, allowed_extensions=field.allowed_extensions,
                         place=field.place, **kwargs)

    @orm.converts('XImageField')
    def conv_ximage(self, model, field, kwargs):
        return XImageField(max_size=field.max_size, allowed_extensions=field.allowed_extensions,
                          place=field.place, **kwargs)

    # @orm.converts('ReferenceField')
    # def conv_Reference(self, model, field, kwargs):
    #     kwargs['allow_blank'] = not field.required

    #     loader = getattr(self.view, '_form_ajax_refs', {}).get(field.name)
    #     if loader:
    #         return AjaxSelectField(loader, **kwargs)

    #     kwargs['widget'] = form.Select2Widget()
    #     queryset = kwargs.get('queryset')
    #     if callable(queryset):
    #         kwargs['queryset'] = queryset(field.document_type)
    #     return orm.ModelConverter.conv_Reference(self, model, field, kwargs)
