from tinydb.table import Table
from tinydb import Query
import bcrypt
import jwt
from time import time
from typing import Dict, List
from node.node_manager import NodeManager


class ActorManager:
    def __init__(self, table: Table, node_manager: NodeManager, vertex: str) -> None:
        self.node_manager = node_manager
        self.table = table
        self.vertex = vertex

    def sign_up(self, node_identifier: str, identifier: str, password: str, actor_type: str, display_name: str, description: str):
        node = self.node_manager.get(node_identifier)
        
        if not node["actor_sign_up_enabled"]:
            raise Exception("Not allowed")

        if self.identifier_exists(identifier, node_identifier):
            raise Exception(f"Actor {identifier} already exists on node {node_identifier}")

        self.table.insert({
            "node_identifier": node_identifier,
            "identifier": identifier,
            "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "type": actor_type,
            "display_name": display_name,
            "description": description,
            "creator": None,
            "created_at": time(),
            "updated_at": time()
        })

        return {
            "identifier": identifier
        }

    def get_token(self, identifier: str, password: str, node_identifier: str, target_node_address: str) -> Dict:
        node_signing_private_key = self.node_manager.get_signing_private_key(node_identifier)
        
        query = Query()
        user = self.table.get((query.identifier == identifier) & (query.node_identifier == node_identifier))
        
        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            raise Exception("Invalid identifier and password combination")
        
        node_address = f"{self.vertex}/{node_identifier}"
        if not target_node_address:
            target_node_address = node_address
        
        return {
            "token": jwt.encode({
                    "sub": identifier,
                    "type": "actor",
                    "iss": node_address,
                    "aud": target_node_address,
                    "iat": int(time())
            }, headers={
                "kid": node_address
            }, key=node_signing_private_key, algorithm="EdDSA")
        }
    
    def get(self, identifier: str, node_identifier: str) -> Dict:
        query = Query()
        actor = self.table.get((query.identifier == identifier) & (query.node_identifier == node_identifier))

        if not actor:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")

        return self.to_dict(actor)
    
    def update(self, identifier: str, display_name: str, description: str, actor_type: str, node_identifier: str):
        fields = {
            "description": description
        }

        if not display_name:
            fields["display_name"] = display_name
        if not actor_type:
            fields["type"] = actor_type
        
        query = Query()
        updates = self.table.update(fields, (query.identifier == identifier) & (query.node_identifier == node_identifier))

        if len(updates) == 0:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")

        return {
            "identifier": identifier
        }
    
    def change_password(self, identifier: str, password: str, node_identifier: str) -> Dict:
        pass

    def delete(self, identifier: str, node_identifier: str) -> Dict:
        query = Query()
        deletes = self.table.remove((query.identifier == identifier & query.node_identifier == node_identifier))
        if len(deletes) == 0:
            raise Exception(f"Actor {identifier} not found on node {node_identifier}")
        return {
            "identifier": identifier
        }

    def identifier_exists(self, identifier: str, node_identifier: str) -> bool:
        query = Query()
        return self.table.contains((query.identifier == identifier) & (query.node_identifier == node_identifier))

    @staticmethod
    def to_dict(self):
        return {
            "identifier": self["identifier"],
            "node_identifier": self["node_identifier"],
            "type": self["type"],
            "display_name": self["display_name"],
            "description": self["description"],
            "creator": self["creator"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"]
        }
