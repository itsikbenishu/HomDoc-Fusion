from entities.abstracts.repository import Repository
from flask import jsonify
from utils.decorators import singleton


@singleton
class HomeDocRepository():
    def __init__(self):
        super().__init__()  

    def get_by_id(self, item_id):
        return jsonify({})
    
    def get(self):
        return jsonify({})

    def create(self, data):
        return jsonify({})

    def update(self, item_id, data):
        return jsonify({})


    def delete(self, item_id):
        return jsonify({})
