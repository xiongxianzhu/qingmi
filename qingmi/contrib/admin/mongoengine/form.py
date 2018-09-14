# coding: utf-8
from flask_mongoengine.wtf import orm
from flask_admin import form
from flask_admin.contrib.mongoengine.form import (CustomModelConverter 
            as _CustomModelConverter)
from flask_admin.model.fields import AjaxSelectField
from wtforms import fields as f

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
