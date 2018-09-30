# coding: utf-8

from flask import current_app
from mongoengine import signals
from mongoengine.base.fields import BaseField
from werkzeug import FileStorage
from qingmi.storage import get_storage
from qingmi.utils import md5
from .generators import RandomGenerator


__all__ = [
    'XFileField', 'XImageField', 'FileProxy', 'ImageProxy',
]


TEXT = ('txt',)

DOCUMENTS = (
    'rtf', 'odf', 'ods', 'gnumeric', 'abw',
    'doc', 'docx', 'xls', 'xlsx'
)

# This contains basic image types that are viewable by most browsers
IMAGES = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp')

# This contains audio file types
AUDIO = ('wav', 'mp3', 'aac', 'ogg', 'oga', 'flac')

# This is for structured data files
DATA = ('csv', 'ini', 'json', 'plist', 'xml', 'yaml', 'yml')

# This contains various types of scripts
SCRIPTS = ('py', 'js', 'rb', 'sh', 'pl', 'php')

# This contains archive and compression formats
ARCHIVES = ('gz', 'bz2', 'zip', 'tar', 'tgz', 'txz', '7z')

# This contains shared libraries and executable files
EXECUTABLES = ('so', 'ext', 'dll')

DEFAULT_EXTENSIONS = TEXT + DOCUMENTS + IMAGES + AUDIO \
                        + DATA + SCRIPTS + ARCHIVES + EXECUTABLES

def is_empty(stream):
    stream.seek(0)
    first_char = stream.read(1)
    stream.seek(0)
    return not bool(first_char)


class FileProxy(object):

    def __init__(self, instance=None, value=None):
        self.instance = instance
        self.filename = ''
        self.process(value)

    def __nonzero__(self):
        return bool(self.filename)

    @property
    def path(self):
        return self.instance.get_path(self.filename)

    @property
    def link(self):
        return self.instance.get_link(self.filename)

    @property
    def content(self):
        return self.instance.get_content(self.filename)

    @property
    def md5(self):
        content = self.content
        if content:
            return md5(content)
        return ''

    def process(self, value=None):
        # print('====', type(value))
        if isinstance(value, FileStorage):
            self._process(stream=value.stream, format=value.filename.split('.')[-1])
        elif isinstance(value, dict):
            self._process(stream=value.get('stream'), format=value.get('format'))
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            self._process(stream=value[0], format=value[1])
        elif isinstance(value, str):
            self._process(filename=value)
        elif hasattr(value, 'read'):
            self._process(stream=value)
        elif not value:
            self._process()
        elif isinstance(value, FileProxy):
            self._process(filename=value.filename)
        else:
            raise ValueError('Can not support type(%s)' % str(value))

    def _process(self, stream=None, format=None, filename=None):
        if stream is not None:
            if not is_empty(stream):
                self.remove()
                if self.instance.is_rename or not self.filename:
                    self.filename = self.instance.put(stream, format=format)
                else:
                    self.instance.put(stream, filename=self.filename)
        elif filename is not None:
            self.remove()
            self.filename = filename
        else:
            self.remove()
            self.filename = ''

    def remove(self):
        self.instance.remove(self.filename)

    def __unicode__(self):
        return self.filename


class XFileField(BaseField):

    proxy_class = FileProxy

    def __init__(self, max_size=2*1024*1024, is_rename=True,
            extensions=None, config_key='STORAGE_SETTINGS',
            place='', filename_generator=None, auto_remove=False,
            **kwargs):
        """Initialises the custom file Field.

        :param config_key:  storage config key in config of app.
        :param filename_generator: filename generator.
        :param auto_remove: upload new file with/without remove old file .
        """
        self.max_size = max_size
        self.is_rename = is_rename
        self.extensions = extensions
        self.config_key = config_key
        self.place = place
        self._filename_generator = filename_generator
        self.auto_remove = auto_remove
        super(XFileField, self).__init__(**kwargs)

    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            config = current_app.config.get(self.config_key)
            if not config:
                raise ValueError('Storage not configured. '
                        'Please set `%s` in config.' % self.config_key)
            self._storage = get_storage(self.config_key, config)
        return self._storage

    @property
    def filename_generator(self):
        if not self._filename_generator:
            self._filename_generator = RandomGenerator()
        return self._filename_generator

    @property
    def is_auto_remove(self):
        if self.auto_remove:
            return self.auto_remove
        return current_app.config.get(self.config_key).get('auto_remove', False)

    def get_path(self, filename):
        if filename:
            return self.storage.get_path(filename)
        return ''

    def get_link(self, filename, **kwargs):
        if filename:
            if filename.startswith('http://') or \
                filename.startswith('https://'):
                return filename
            return self.storage.get_link(filename, **kwargs)
        return ''

    def get_content(self, filename):
        if filename:
            return self.storage.read(filename)

    def put(self, stream, filename=None, format=None, **kwargs):
        if not filename:
            filename = self.filename_generator()
            if format:
                filename = '{}.{}'.format(filename, format)
        self.storage.write(filename, stream.read())
        return filename

    def remove(self, filename):
        if filename and self.is_auto_remove:
            self.storage.delete(filename)

    def register_signals(self, instance):
        if not hasattr(self, '_instance') and instance is not None:
            self._instance = instance
            signals.pre_delete.connect(self.pre_delete, sender=self._instance.__class__)

    def pre_delete(self, sender, document, **kwargs):
        obj = document._data.get(self.name)
        if isinstance(obj, self.proxy_class) and self.is_auto_remove:
            obj.remove()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.name)
        if not isinstance(value, self.proxy_class) or value is None:
            value = self.proxy_class(self, value)
            instance._data[self.name] = value
        return instance._data[self.name]

    def __set__(self, instance, value):
        self.register_signals(instance)

        key = self.name
        obj = instance._data.get(key)
        if isinstance(value, self.proxy_class) and value.instance == self:
            if obj and id(obj) != value and str(value) != str(value):
                self.__get__(instance).remove()
            instance._data[key] = value
        elif not isinstance(obj, self.proxy_class):
            obj = self.proxy_class(self, obj)
            obj.process(value)
            instance._data[key] = obj
        else:
            obj.process(value)
        instance._mark_as_changed(key)


    def to_mongo(self, value):
        if isinstance(value, self.proxy_class):
            return value.filename
        return value

    def to_python(self, value):
        if not isinstance(value, self.proxy_class):
            return self.proxy_class(self, value)
        return value



class ImageProxy(FileProxy):

    @property
    def link(self):
        return self.instance.get_link(self.filename)


class XImageField(XFileField):

    proxy_class = ImageProxy
