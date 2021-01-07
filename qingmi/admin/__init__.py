# coding: utf-8
from flask_admin import Admin as _Admin, AdminIndexView

ADMIN_MENUS_JSON = """"""


class Admin(_Admin):

    def __init__(self, app=None, name=None,
                 url=None, subdomain=None,
                 index_view=None,
                 translations_path=None,
                 endpoint=None,
                 static_url_path=None,
                 base_template=None,
                 template_mode=None,
                 category_icon_classes=None):
        super(Admin, self).__init__(
            app=app, name=name,
            url=url, subdomain=subdomain,
            index_view=index_view,
            translations_path=translations_path,
            endpoint=endpoint,
            static_url_path=static_url_path,
            base_template=base_template,
            template_mode=template_mode,
            category_icon_classes=category_icon_classes,
        )

    def _set_admin_index_view(self, index_view=None,
                              endpoint=None, url=None):
        self.index_view = (index_view or self.index_view or
                           AdminIndexView(endpoint=endpoint, url=url))
        self.endpoint = endpoint or self.index_view.endpoint
        self.url = url or self.index_view.url

        if len(self._views) > 0:
            self._views[0] = self.index_view
        else:
            self.add_view(self.index_view)
