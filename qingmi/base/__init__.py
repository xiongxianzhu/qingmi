# coding: utf-8

from flask import Blueprint, current_app
from qingmi.db.mongoengine import MongoEngine
from flask_caching import Cache
from flask_bcrypt import Bcrypt


db = MongoEngine()
cache = Cache()
bcrypt = Bcrypt()
