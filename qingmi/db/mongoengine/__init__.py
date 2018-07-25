# coding: utf-8

from flask_mongoengine import (MongoEngine as _MongoEngine,
                                BaseQuerySet as _BaseQuerySet,
                                Document as _Document,
                                DynamicDocument as _DynamicDocument)
from . import pagination


class Chocies(object):

    def __init__(self, **kwargs):
        self.CHOICES = []
        for key, value in kwargs.items():
            self.CHOICES.append((key, value))
            setattr(self, key.upper(), key)
        self.DICT = dict(self.CHOICES)
        self.VALUES = self.DICT.keys()

    def text(self, key):
        return self.DICT.get(key)


class MongoEngine(_MongoEngine):

    def __init__(self, app=None, config=None):
        super(MongoEngine, self).__init__(app)

        self.Document = Document
        self.DynamicDocument = DynamicDocument

    def choices(self, **kwargs):
        return Chocies(**kwargs)


class BaseQuerySet(_BaseQuerySet):

    def paginate(self, **kwargs):
        return pagination.Pagination(self, **kwargs)


class Document(_Document):

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}


class DynamicDocument(_DynamicDocument):

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}