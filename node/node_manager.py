from tinydb.table import Table
from tinydb import Query
from typing import Dict, List
from time import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from utils.ed25519 import Ed25519


class NodeManager:
    def __init__(self, table: Table) -> None:
        self.table = table

    def create(self, identifier: str, display_name: str, description: str, actor_sign_up_enabled: bool, creator: str) -> Dict:
        if self.identifier_exists(identifier):
            raise Exception(f"Node {identifier} already exists")
        
        signing_key = Ed25519.generate()
        signing_pubic_key = Ed25519.encode_public_key(signing_key.public_key())

        self.table.insert({
            "identifier": identifier,
            "display_name": display_name,
            "description": description,
            "actor_sign_up_enabled": actor_sign_up_enabled,
            "signing_private_key": Ed25519.encode_private_key(signing_key),
            "signing_public_key": signing_pubic_key,
            "creator": creator,
            "created_at": time(),
            "updated_at": time()
        })

        return {
            "identifier": identifier,
            "signing_public_key": signing_pubic_key
        }

    def list(self) -> List:
        nodes = self.table.all()
        results = []
        for node in nodes:
            results.append(self.to_dict(node))
        return results

    def get(self, identifier: str) -> Dict:
        query = Query()
        node = self.table.get(query.identifier == identifier)
        if not node:
            raise Exception(f"Node {identifier} not found")
        return self.to_dict(node)
    
    def get_signing_private_key(self, identifier: str) -> ed25519.Ed25519PrivateKey:
        query = Query()
        node = self.table.get(query.identifier == identifier)
        if not node:
            raise Exception(f"Node {identifier} not found")
        
        return Ed25519.decode_private_key(node["signing_private_key"])
    
    def get_signing_public_key(self, identifier: str) -> ed25519.Ed25519PublicKey:
        return Ed25519.decode_public_key(self.get(identifier)["signing_public_key"])

    def update(self, identifier: str, display_name: str, description: str):
        fields = {
            "updated_at": time(),
            "description": description
        }

        if display_name:
            fields["display_name"] = display_name

        query = Query()
        results = self.table.update(fields, query.identifier == identifier)
        
        if len(results) == 0:
            raise Exception(f"Node {identifier} not found")
        
        return {
            "identifier": identifier
        }

    def change_actor_sign_up_enabled(self, identifier: str, actor_sign_up_enabled: bool) -> Dict:
        fields = {
            "actor_sign_up_enabled": actor_sign_up_enabled,
            "updated_at": time()
        }
        
        query = Query()
        results = self.table.update(fields, query.identifier == identifier)
        
        if len(results) == 0:
            raise Exception(f"Node {identifier} not found")
        
        return {
            "identifier": identifier
        }

    def reset_signing_keys(self, identifier: str) -> Dict:
        signing_key = Ed25519.generate()
        signing_pubic_key = Ed25519.encode_public_key(signing_key.public_key())

        fields = {
            "updated_at": time(),
            "signing_public_key": signing_pubic_key,
            "signing_private_key": Ed25519.encode_private_key(signing_key)
        }

        query = Query()
        results = self.table.update(fields, query.identifier == identifier)
        
        if len(results) == 0:
            raise Exception(f"Node {identifier} not found")
        
        return {
            "identifier": identifier,
            "signing_public_key": signing_pubic_key
        }

    def delete(self, identifier: str) -> Dict:
        query = Query()
        deleted = self.table.remove(query.identifier == identifier)
        if len(deleted) == 0:
            raise Exception(f"Node {identifier} not found")
        return {
            "identifier": identifier
        }

    def identifier_exists(self, identifier: str):
        query = Query()
        return self.table.contains(query.identifier == identifier)

    @staticmethod
    def to_dict(self) -> Dict:
        return {
            "identifier": self["identifier"],
            "display_name": self["display_name"],
            "description": self["description"],
            "signing_public_key": self["signing_public_key"],
            "actor_sign_up_enabled": self["actor_sign_up_enabled"],
            "creator": self["creator"],
            "created_at": self["created_at"],
            "updated_at": self["updated_at"]
        }
