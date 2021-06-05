from flask import Flask, jsonify, request

class User:
    def signup(self):
        user = {
            "_id":"",
            "name":"",
            "email":"",
            "password":""
        }

        return jsonify(user), 200