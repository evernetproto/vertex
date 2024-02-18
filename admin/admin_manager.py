from tinydb.table import Table
from tinydb import Query
import bcrypt
from typing import Dict, List
from time import time
import jwt
from password_generator import PasswordGenerator

class AdminManager:
    def __init__(self, table: Table, vertex: str, jwt_signing_key: str) -> None:
        self.table = table
        self.vertex = vertex
        self.jwt_signing_key = jwt_signing_key
        self.password_generator = PasswordGenerator()

    def initialize(self, username: str, password: str) -> Dict:
        if len(self.table.all()) != 0:
            raise Exception("Not allowed")

        self.table.insert({
            "username": username,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "creator": None,
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
    
    def get(self, username: str) -> Dict:
        query = Query()
        admin = self.table.get(query.username == username)
        if not admin:
            raise Exception(f"Admin {username} not found")
        return self.to_dict(admin)
    
    def change_password(self, username: str, password: str) -> Dict:
        fields = {
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "updated_at": time()
        }

        query = Query()
        updates = self.table.update(fields, query.username == username)
        
        if len(updates) == 0:
            raise Exception("Admin not found")
        
        return {
            "username": username
        }

    def add(self, username: str, creator: str) -> Dict:
        if self.username_exists(username):
            raise Exception(f"Username {username} is already taken")

        password = self.password_generator.generate()

        self.table.insert({
            "username": username,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "creator": creator,
            "created_at": time(),
            "updated_at": time()
        })
        
        return {
            "username": username,
            "password": password
        }

    def username_exists(self, username: str) -> bool:
        query = Query()
        return self.table.contains(query.username == username)

    @staticmethod
    def to_dict(self) -> Dict:
        return {
            "username": self["username"],
            "creator": self["creator"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"]
        }