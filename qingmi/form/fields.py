# coding: utf-8
from werkzeug.datastructures import FileStorage
from wtforms.fields import Field, FileField, TextAreaField
from wtforms.utils import unset_value
from wtforms.validators import ValidationError
from .widgets import FileInput, ImageInput, WangEditor, AreaInput


__all__ = [
    'XFileField', 'XImageField', 'WangEditorField',
]

DEFAULT_EXTENSIONS = ['txt', 'bz2', 'gz', 'tar', 'zip', 'rar', 'apk', 'jpg', 'jpeg', 'png', 'gif', 'bmp']
DEFAULT_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']


class XFileField(FileField):

    widget = FileInput()

    def __init__(self, label=None, max_size=None,
            allowed_extensions=None, place=None, **kwargs):
        self._should_delete = False
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or DEFAULT_EXTENSIONS
        self.place = place
        super(XFileField, self).__init__(label=label, **kwargs)

    def _is_uploaded_file(self, data):
        return (data and isinstance(data, FileStorage) and data.filename)

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.

            :param filename:
                File name to check
        """
        if not self.allowed_extensions:
            return True

        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in
                map(lambda x: x.lower(), self.allowed_extensions))

    def pre_validate(self, form, extra_validators=tuple()):
        # Handle overwriting existing content
        if not self._is_uploaded_file(self.data):
            return
        # if not self.data:
        #     return

        file_format = self.data.filename.split('.')[-1]
        # if self.allowed_extensions and file_format.lower() not in self.allowed_extensions:
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError('%s 格式不支持上传' % file_format)

        # print('========', self.max_size, self.data, self.data.headers, self.data.content_length)

        if self.max_size and self.data.content_length > self.max_size:
            raise ValidationError('文件太大(%d/%d)' % (
                self.max_size, self.data.content_length))

    def process(self, formdata, data=unset_value):
        """
        Process incoming data, calling process_data, process_formdata as needed,
        and run filters.
        If `data` is not provided, process_data will be called on the field's
        default.
        Field subclasses usually won't override this, instead overriding the
        process_formdata and process_data methods. Only override this for
        special advanced processing, such as when a field encapsulates many
        inputs.
        """
        self.process_errors = []
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata is not None:
            if self.name in formdata:
                self.raw_data = formdata.getlist(self.name)
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

            marker = '%s-delete' % self.name
            if marker in formdata:
                self._should_delete = True

        try:
            for filter in self.filters:
                self.data = filter(self.data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

    def is_empty(self):
        if self.data:
            self.data.stream.seek(0)
            first_char = self.data.stream.read(1)
            self.data.stream.seek(0)
            return not bool(first_char)
        return True

    def populate_obj(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.
        :note: This is a destructive operation. If `obj.<name>` already exists,
               it will be overridden. Use with caution.
        """
        # setattr(obj, name, self.data)
        if self.data and not self.is_empty():
            setattr(obj, name, self.data)
        elif self._should_delete:
            setattr(obj, name, None)


class XImageField(XFileField):

    widget = ImageInput()

    def __init__(self, label=None, max_size=None,
            allowed_extensions=DEFAULT_IMAGE_EXTENSIONS, place=None, **kwargs):
        super(XImageField, self).__init__(label=label, max_size=max_size,
            allowed_extensions=allowed_extensions,
            place=place, **kwargs)


class WangEditorField(TextAreaField):
    widget = WangEditor()


class AreaField(Field):

    widget = AreaInput()
    defaults = dict(province=u'省份', city=u'城市', county=u'县/区')

    def process(self, formdata, data=unset_value):
        self.process_errors = []
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata:
            area = []
            for field in ['province', 'city', 'county']:
                name = '%s_%s' % (self.name, field)
                data = formdata.get(name, '').strip()
                if data.strip() and data != self.defaults.get(field):
                    area.append(data)
            if len(area) == 3:
                self.data = '|'.join(area)
