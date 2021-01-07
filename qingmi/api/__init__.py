# coding: utf-8

from flask_restful import Resource as _Resource, reqparse


class Resource(_Resource):

    def __init__(self):
        super(Resource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.add_args()

    def add_args(self):
        pass

    def get_args(self):
        return self.parser.parse_args()
