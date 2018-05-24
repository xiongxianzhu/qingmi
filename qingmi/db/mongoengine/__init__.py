# coding: utf-8
from __future__ import unicode_literals

from flask_mongoengine import (MongoEngine as _MongoEngine,
                                BaseQuerySet as _BaseQuerySet,
                                Document as _Document,
                                DynamicDocument as _DynamicDocument)
from . import pagination


class MongoEngine(_MongoEngine):

    def __init__(self, app=None, config=None):
        super(MongoEngine, self).__init__(app)

        self.Document = Document
        self.DynamicDocument = DynamicDocument


class BaseQuerySet(_BaseQuerySet):

    def paginate(self, **kwargs):
        return pagination.Pagination(self, **kwargs)


class Document(_Document):

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}


class DynamicDocument(_DynamicDocument):

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}