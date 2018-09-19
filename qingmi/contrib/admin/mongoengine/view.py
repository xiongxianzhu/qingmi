# coding: utf-8
from datetime import datetime
from flask import request, flash, redirect
from flask_admin.babel import gettext
from flask_admin.base import expose
from flask_admin.contrib.mongoengine import ModelView as _ModelView
from flask_admin.model.base import BaseModelView
from flask_admin.helpers import get_redirect_target
from flask_admin._compat import string_types
from blinker import signal
from jinja2 import contextfunction
from flask_login import current_user
from mongoengine.fields import StringField
from qingmi.contrib.admin.mongoengine.filters import FilterConverter
from qingmi.contrib.admin.mongoengine import AdminChangeLog
from qingmi.contrib.admin.mongoengine.form import CustomModelConverter
from qingmi.admin.formatters import formatter_text, bool_formatter
from qingmi.utils import json_success, json_error


def model_changed(flag, model, **kwargs):
    user = current_user.id
    if flag == 'update':
        AdminChangeLog.change_data(user, model=model, **kwargs)
    elif flag == 'dropdown':
        # AdminChangeLog.dropdown_modify(user, model=model, **kwargs)
        AdminChangeLog.change_data(user, model=model, **kwargs)

model_change_signal = signal('model-change-signal')
model_change_signal.connect(model_changed)


class ModelView(_ModelView):

    page_size = 50
    can_edit = True
    can_view_details = True
    can_delete = True
    edit_modal = True
    details_modal = True

    column_type_formatters = _ModelView.column_type_formatters or dict()
    model_form_converter = CustomModelConverter
    filter_converter = FilterConverter()

    def __init__(self, model, name=None,
                 category=None, endpoint=None, url=None, static_folder=None,
                 menu_class_name=None, menu_icon_type=None, menu_icon_value=None):
        # 初始化字段标识
        self.init_column_labels(model)
        # 初始化字段类型格式化
        self.init_column_formatters(model)

        super(ModelView, self).__init__(model, name, category, endpoint, url, static_folder,
                                        menu_class_name=menu_class_name,
                                        menu_icon_type=menu_icon_type,
                                        menu_icon_value=menu_icon_value)

    def init_column_labels(self, model):
        """ 初始化标识 """
        self.column_labels = self.column_labels or dict()
        self.column_labels.setdefault('id', 'ID')
        for field in model._fields:
            if field not in self.column_labels:
                attr = getattr(model, field)
                if hasattr(attr, 'verbose_name'):
                    verbose_name = attr.verbose_name
                    if verbose_name:
                        self.column_labels[field] = verbose_name

    def init_column_formatters(self, model):
        """ 初始化字段类型格式化 """
        for field in model._fields:
            attr = getattr(model, field)
            if type(attr) == StringField:
                self.column_formatters.setdefault(attr.name, formatter_text(40))

    def scaffold_filters(self, name):
        """
            Return filter object(s) for the field

            :param name:
                Either field name or field instance
        """
        if isinstance(name, string_types):
            attr = self.model._fields.get(name)
        else:
            attr = name

        if attr is None:
            raise Exception('Failed to find field for filter: %s' % name)

        # Find name
        visible_name = None

        if not isinstance(name, string_types):
            visible_name = self.get_column_name(attr.name)

        if not visible_name:
            visible_name = self.get_column_name(name)

        # Convert filter
        type_name = type(attr).__name__
        flt = self.filter_converter.convert(type_name,
                                            attr,
                                            visible_name)

        return flt

    def create_model(self, form):
        """
            Create model helper

            :param form:
                Form instance
        """
        try:
            model = self.model()
            self.before_model_change(form, model, True)
            form.populate_obj(model)
            self._on_model_change(form, model, True)
            model.save()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to create record. %(error)s',
                              error=format_error(ex)),
                      'error')
                log.exception('Failed to create record.')

            return False
        else:
            self.after_model_change(form, model, True)

        return model

    def update_model(self, form, model):
        """
            Update model helper

            :param form:
                Form instance
            :param model:
                Model instance to update
        """
        try:
            self.before_model_change(form, model, False)
            form.populate_obj(model)
            self._on_model_change(form, model, False)
            model.save()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to update record. %(error)s',
                              error=format_error(ex)),
                      'error')
                log.exception('Failed to update record.')

            return False
        else:
            self.after_model_change(form, model, False)

        return True

    def delete_model(self, model):
        """
            Delete model helper

            :param model:
                Model instance
        """
        try:
            self.on_model_delete(model)
            model.delete()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s',
                              error=format_error(ex)),
                      'error')
                log.exception('Failed to delete record.')

            return False
        else:
            self.after_model_delete(model)

        return True
    

    def _refresh_cache(self):
        self.column_choices = self.column_choices or dict()
        for field in self.model._fields:
            choices = getattr(self.model, field).choices
            if choices:
                self.column_choices[field] = choices
        super(ModelView, self)._refresh_cache()

    # def _process_ajax_references(self):
    #     references = BaseModelView._process_ajax_references(self)
    #     return process_ajax_references(references, self)
    
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('Record does not exist.'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                flash(gettext('删除记录成功。'), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Failed to delete record. %(error)s')

        return redirect(return_url)

    @expose('/ajax/update/', methods=('POST',))
    def ajax_update(self):
        """
            Edits a single column of a record in list view.
        """
        if not self.column_editable_list:
            abort(404)

        form = self.list_form()

        # prevent validation issues due to submitting a single field
        # delete all fields except the submitted fields and csrf token
        for field in list(form):
            if (field.name in request.form) or (field.name == 'csrf_token'):
                pass
            else:
                form.__delitem__(field.name)

        if self.validate_form(form):
            pk = form.list_form_pk.data
            record = self.get_one(pk)

            if record is None:
                return gettext('Record does not exist.'), 500

            if self.update_model(form, record):
                # Success
                return gettext('Record was successfully saved.')
            else:
                # Error: No records changed, or problem saving to database.
                msgs = ", ".join([msg for msg in get_flashed_messages()])
                return gettext('Failed to update record. %(error)s',
                               error=msgs), 500
        else:
            for field in form:
                for error in field.errors:
                    # return validation error to x-editable
                    if isinstance(error, list):
                        return gettext('Failed to update record. %(error)s',
                                       error=", ".join(error)), 500
                    else:
                        return gettext('Failed to update record. %(error)s',
                                       error=error), 500

    def before_model_change(self, form, model, is_created):

        pass

    # Model event handlers
    def on_model_change(self, form, model, is_created):
        """
            Perform some actions before a model is created or updated.

            Called from create_model and update_model in the same transaction
            (if it has any meaning for a store backend).

            By default does nothing.

            :param form:
                Form used to create/update model
            :param model:
                Model that will be created/updated
            :param is_created:
                Will be set to True if model was created and to False if edited
        """
        pass

    def after_model_change(self, form, model, is_created):
        """
            Perform some actions after a model was created or updated and
            committed to the database.

            Called from create_model after successful database commit.

            By default does nothing.

            :param form:
                Form used to create/update model
            :param model:
                Model that was created/updated
            :param is_created:
                True if model was created, False if model was updated
        """
        pass

    def on_model_delete(self, model):
        """
            Perform some actions before a model is deleted.

            Called from delete_model in the same transaction
            (if it has any meaning for a store backend).

            By default do nothing.
        """
        pass

    def after_model_delete(self, model):
        """
            Perform some actions after a model was deleted and
            committed to the database.

            Called from delete_model after successful database commit
            (if it has any meaning for a store backend).

            By default does nothing.

            :param model:
                Model that was deleted
        """
        pass

    @contextfunction
    def get_detail_value(self, context, model, name):
        column_fmt = self.column_formatters.get(name)
        if column_fmt is not None:
            try:
                value = column_fmt(self, context, model, name)
            except:
                value = '该对象被删了'
        else:
            try:
                value = self._get_field_value(model, name)
            except:
                value = '该对象被删了'

        choices_map = self._column_choices_map.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        # format column value for bool type
        # if isinstance(value, bool):
        #     return bool_formatter(self, value, model, name, False, 'detail')

        type_fmt = None
        for typeobj, formatter in self.column_type_formatters.items():
            if isinstance(value, typeobj):
                type_fmt = formatter
                break
        if type_fmt is not None:
            try:
                value = type_fmt(self, value)
            except:
                value = '该对象被删了'

        return value

    @contextfunction
    def get_list_value(self, context, model, name):
        """
            Returns the value to be displayed in the list view

            :param context:
                :py:class:`jinja2.runtime.Context`
            :param model:
                Model instance
            :param name:
                Field name
        """
        # print('get_list_value#####', model._fields.get(name))
        # column = model._fields.get(name)
        # print('get_list_value#####', type(column))
        # print('get_list_value#####', column_fmt)

        column_fmt = self.column_formatters.get(name)
        if column_fmt is not None:
            try:
                value = column_fmt(self, context, model, name)
            except:
                value = '该对象被删了'
        else:
            try:
                value = self._get_field_value(model, name)
            except:
                value = '该对象被删了'

        choices_map = self._column_choices_map.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        # format column value for bool type
        if isinstance(value, bool):
            return bool_formatter(self, value, model, name)

        type_fmt = None
        for typeobj, formatter in self.column_type_formatters.items():
            if isinstance(value, typeobj):
                type_fmt = formatter
                break
        if type_fmt is not None:
            try:
                value = type_fmt(self, value)
            except:
                value = '该对象被删了'

        return value

    def on_field_change(self, model, name, value):
        model[name] = value
        if hasattr(model, 'updated_at'):
            model['updated_at'] = datetime.now()

    @expose('/ajax/change/', methods=('GET',))
    def ajax_change(self):
        """ 异步改变列表中记录的某个字段的值 """
        id = request.args.get('id', 0, str)
        val = request.args.get('key', '')
        name = request.args.get('name', '', str)
        value = request.args.get('value', '', str)
        model = self.model

        if not current_user.is_authenticated:
            return json_error()

        if not val:
            val = False if value == 'False' else True
        if type(val) == int:
            val = int(val)

        obj = model.objects(id=id).first()
        if obj:
            before_data = obj[name]
            self.on_field_change(obj, name, val)
            obj.save()
            # model_signals.send(
            #     'dropdown', model=model, key=name,
            #     before_data=before_data, after_data=val, id=id)
            return json_success()

        return json_error(msg='该记录不存在')