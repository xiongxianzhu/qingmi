# coding: utf-8
"""Local storage, save the file in local directory.
"""

import os
from qingmi._compat import urljoin
from qingmi.utils import file
from .base import BaseStorage
from .utils import ConfigItem


class LocalStorage(BaseStorage):
    """Storage for local filesystem."""

    base_path = ConfigItem('base_path', required=True)
    base_dir = ConfigItem('base_dir', default='')

    def __init__(self, config=None):
        super(LocalStorage, self).__init__(config)

    def get_path(self, filename, base_dir=None):
        filename = os.path.join(base_dir or self.base_dir, filename)
        file_path = urljoin(self.base_path, filename)
        return file_path

    def read(self, filename):
        return file.read(self.get_path(filename))

    def write(self, filename, body):
        return file.write(self.get_path(filename), body)

    def delete(self, filename):
        return file.delete(self.get_path(filename))
