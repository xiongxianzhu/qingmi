# coding: utf-8
from wtforms.fields import FileField
from wtforms.utils import unset_value
from wtforms.validators import ValidationError
from .widgets import FileInput, ImageInput


__all__ = [
    'XFileField', 'XImageField',
]

DEFAULT_EXTENSIONS = ['txt', 'bz2', 'gz', 'tar', 'zip', 'rar', 'apk', 'jpg', 'jpeg', 'png', 'gif', 'bmp']
DEFAULT_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']


class XFileField(FileField):

    widget = FileInput()

    def __init__(self, label=None, max_size=None,
            extensions=DEFAULT_EXTENSIONS, place=None, **kwargs):
        self.delete = False
        self.max_size = max_size
        self.extensions = extensions
        self.place = place
        super(XFileField, self).__init__(label=label, **kwargs)

    def pre_validate(self, form, extra_validators=tuple()):
        if not self.data:
            return

        format = self.data.filename.split('.')[-1]
        if self.extensions and format.lower() not in self.extensions:
            raise ValidationError('%s 格式不支持上传' % format)

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

            key = '%s-delete' % self.name
            if formdata.get(key) == 'true':
                self.delete = True

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
        elif self.delete:
            setattr(obj, name, None)


class XImageField(XFileField):

    widget = ImageInput()

    def __init__(self, label=None, max_size=None,
            extensions=DEFAULT_IMAGE_EXTENSIONS, place=None, **kwargs):
        super(XImageField, self).__init__(label=label, **kwargs)

    