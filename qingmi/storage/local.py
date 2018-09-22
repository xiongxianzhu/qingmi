# coding: utf-8
"""Local storage, save the file in local directory.
"""

import os
from qingmi._compat import urljoin
from qingmi.utils import file
from qingmi.storage.base import BaseStorage
from qingmi.storage.utils import ConfigItem


class LocalStorage(BaseStorage):
    """Storage for local filesystem."""

    storage_type = ConfigItem('storage_type', required=True)
    base_path = ConfigItem('base_path', required=True)
    base_dir = ConfigItem('base_dir', default='')
    base_url = ConfigItem('base_url', default='')

    def __init__(self, config=None):
        super(LocalStorage, self).__init__(config)
        self.baseurl = self.config.get('base_url')

    def url(self, filename):
        return os.path.join(self.baseurl, filename)
        # return urljoin(self.baseurl, filename)

    def read(self, filename):
        return file.read(self.url(filename))

    def write(self, filename, body):
        return file.write(self.url(filename), body)

    def delete(self, filename):
        return file.delete(self.url(filename))
