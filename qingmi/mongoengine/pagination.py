# coding: utf-8
from flask import request, url_for, render_template
from flask_mongoengine.pagination import Pagination as _Pagination
from ..helper import success

class Pagination(_Pagination):

    def json(self, tojson=lambda x: x.json, **kwargs):
        return success(
            items=[tojson(x) for x in self.items], **kwargs)
