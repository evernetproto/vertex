from tinydb.table import Table
from tinydb import Query
import bcrypt
from typing import Dict, List
from time import time

class AdminManager:
    def __init__(self, table: Table) -> None:
        self.table = table

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
