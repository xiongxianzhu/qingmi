# coding: utf-8

from flask import current_app
from mongoengine import signals
from mongoengine.base.fields import BaseField
from werkzeug import FileStorage
from qingmi.storage import get_storage


__all__ = [

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


class FileProxy(object):

    def __init__(self, instance=None):
        self.instance = instance

    pass


class XFileField(BaseField):

    proxy_class = FileProxy

    def __init__(self, config_key='STORAGE_SETTINGS', extensions=None,
            filename_generator=None, **kwargs):
        """Initialises the custom file Field.

        :param config_key:  storage config key in config of app.
        :param filename_generator: filename generator.
        """
        self.config_key = config_key
        self.extensions = extensions
        self.filename_generator = filename_generator
        super(XFildField, self).__init__(**kwargs)

    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            config = current_app.config.get(self.config_key)
            if not config:
                raise ValueError('Storage not configured. '
                        'Please set `%s` in config.' % self.config_key)
            self._storage = get_storage(self.config_key, config)
        return self._storage

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.name)
        return instance._data[self.name]



class ImageProxy(FileProxy):

    pass


class XImageField(XFileField):

    proxy_class = ImageProxy

    pass