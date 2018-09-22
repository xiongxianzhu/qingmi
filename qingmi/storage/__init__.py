# coding: utf-8

from werkzeug.utils import import_string
from qingmi.storage.local import LocalStorage

storages = {
    'local': 'qingmi.storage.local.LocalStorage',
    # 'oss': 'qingmi.storage.aliyunoss.OSSStorage', # todo
}


class Storage(object):
    """Create a storage instance.
    :param app: Flask app instance
    """

    def __init__(self, app=None):
        self._storage = None
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        config = app.config.get('STORAGE_SETTINGS', {})
        
        t = config.setdefault('storage_type', 'local')
        tpl = "Storage type: %r. Storage type not supported."
        assert t in storages, tpl % t

        storage_model = import_string(storages[t])
        self._storage = storage_model(config)

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if self._storage is None:
                raise RuntimeError("Storage not configured.")
            return getattr(self._storage, key)


def _get_storage(config):
    t = config.setdefault('storage_type', 'local')
    tpl = "Storage type: %r. Storage type not supported."
    assert t in storages, tpl % t

    if t == 'local':
        return LocalStorage(config)
    raise ValueError('Storage type (%s) not supported.' % config['type'])


_storages = {}


def get_storage(key, config):
    global _storages
    if key not in _storages:
        _storages[key] = _get_storage(config)
    return _storages[key]
