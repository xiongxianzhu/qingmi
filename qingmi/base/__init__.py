# coding: utf-8

from flask import Blueprint, current_app
from ..db.mongoengine import MongoEngine
from flask_caching import Cache


db = MongoEngine()
cache = Cache()
