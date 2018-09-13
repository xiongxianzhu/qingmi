# coding: utf-8
from flask import request, flash, redirect
from flask_admin.babel import gettext
from flask_admin.base import expose
from flask_admin.contrib.mongoengine import ModelView as _ModelView
from flask_admin.model.base import BaseModelView
from flask_admin.helpers import get_redirect_target
from blinker import signal
from flask_login import current_user
from qingmi.contrib.admin.mongoengine.filters import FilterConverter
from qingmi.contrib.admin.mongoengine import AdminChangeLog


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

    filter_converter = FilterConverter()

    # def scaffold_filters(self, name):
    #     """
    #         Return filter object(s) for the field

    #         :param name:
    #             Either field name or field instance
    #     """
    #     if isinstance(name, string_types):
    #         attr = self.model._fields.get(name)
    #     else:
    #         attr = name

    #     if attr is None:
    #         raise Exception('Failed to find field for filter: %s' % name)

    #     # Find name
    #     visible_name = None

    #     if not isinstance(name, string_types):
    #         visible_name = self.get_column_name(attr.name)

    #     if not visible_name:
    #         visible_name = self.get_column_name(name)

    #     # Convert filter
    #     type_name = type(attr).__name__
    #     flt = self.filter_converter.convert(type_name,
    #                                         attr,
    #                                         visible_name)

    #     return flt
    

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
