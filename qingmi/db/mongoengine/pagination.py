# coding: utf-8
from flask import abort, request, url_for, render_template
from flask_mongoengine.pagination import Pagination as _Pagination
from qingmi.utils import success

class Pagination(_Pagination):

    def __init__(self, iterable, page=None, per_page=None,
                    endpoint=None, **kwargs):
        if page < 1:
            abort(404)
        page = page or max(1, request.args.get('page', 1, int))
        per_page = per_page or max(1, min(100,
                    request.args.get('per_page', 10, int)))
        super(Pagination, self).__init__(iterable, page, per_page)
        self.endpoint = endpoint if endpoint else request.endpoint
        self.kwargs = kwargs

    @property
    def has_pages(self):
        return self.pages > 1

    @property
    def next_link(self):
        if self.has_next:
            return self.get_link(self.next_num)
        return ''

    def get_link(self, page):
        return url_for(self.endpoint, page=page, per_page=self.per_page,
                        **self.kwargs)

    def json(self, tojson=lambda x: x.json, **kwargs):
        return success(
            items=[tojson(x) for x in self.items],
            next=self.next_link, **kwargs)
