from tinydb.table import Table
from tinydb import Query
import bcrypt
from typing import Dict, List
from time import time
import jwt

class AdminManager:
    def __init__(self, table: Table, vertex: str, jwt_signing_key: str) -> None:
        self.table = table
        self.vertex = vertex
        self.jwt_signing_key = jwt_signing_key

    def initialize(self, username: str, password: str) -> Dict:
        if len(self.table.all()) != 0:
            raise Exception("Not allowed")

        self.table.insert({
            "username": username,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "created_at": time(),
            "updated_at": time()
        })

        return {
            "username": username
        }

    def get_token(self, username: str, password: str) -> Dict:
        query = Query()
        admin = self.table.get(query.username == username)
        
        if not admin or not bcrypt.checkpw(password.encode("utf-8"), admin["password"].encode("utf-8")):
            raise Exception("Invalid username and password combination")

        return {
            "token": jwt.encode({
                "sub": admin["username"],
                "type": "admin",
                "iat": int(time()),
                "iss": self.vertex,
                "aud": self.vertex
            }, key=self.jwt_signing_key, algorithm="HS256")
        }