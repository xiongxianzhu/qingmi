# coding: utf-8

import os
import logging
from werkzeug import FileStorage
from qingmi._compat import urljoin


__all__ = (
    'TEXT', 'DOCUMENTS', 'IMAGES', 'AUDIO', 'DATA', 'SCRIPTS',
    'ARCHIVES', 'EXECUTABLES', 'BaseStorage',
)

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


class BaseStorage(object):

    def __init__(self, config=None):
        self.config = config
        self.extensions = self.config.get('extensions', IMAGES)

    def path(self, filename):
        """Generate the url for a filename.
        :param filename: filename for generating the url....
        """
        base_path = self.config.get('base_path')
        return urljoin(base_path, filename)

    def extension_allowed(self, extname):
        if not self.extensions:
            return True
        return extname in self.extensions

    def read(self, filename):
        raise NotImplementedError

    def write(self, filename, body):
        raise NotImplementedError

    def delete(self, filename):
        raise NotImplementedError