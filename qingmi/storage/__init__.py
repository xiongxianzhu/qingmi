# coding: utf-8
import os
from flask import send_from_directory
from werkzeug.utils import import_string
from qingmi.storage.local import LocalStorage
from qingmi._compat import urljoin


storages = {
    'local': 'qingmi.storage.local.LocalStorage',
    # 'oss': 'qingmi.storage.aliyunoss.OSSStorage', # todo
}


class Storage(object):
    """Create a storage instance.
    :param app: Flask app instance
    """

    def __init__(self, app=None, config_key='STORAGE_SETTINGS'):
        self._storage = None
        self.config_key = config_key
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app, config_key='STORAGE_SETTINGS'):
        self.config_key = config_key
        config = app.config.get(config_key, {})
        
        t = config.setdefault('storage_type', 'local')
        tpl = "Storage type: %r. Storage type not supported."
        assert t in storages, tpl % t

        storage_model = import_string(storages[t])
        self._storage = storage_model(config)

        if t == 'local':
            @app.route(config['base_link'] % '<path:filename>', endpoint=self.config_key.lower())
            def upload(filename):
                # return send_from_directory(urljoin(config['base_path'], config['base_dir']), filename)
                return send_from_directory(os.path.join(config['base_path'], config['base_dir']), filename)

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
