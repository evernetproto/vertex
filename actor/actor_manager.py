from tinydb.table import Table
from tinydb import Query
import bcrypt
from time import time
from node.node_manager import NodeManager


class ActorManager:
    def __init__(self, table: Table, node_manager: NodeManager) -> None:
        self.node_manager = node_manager
        self.table = table

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

    def identifier_exists(self, identifier: str, node_identifier: str):
        query = Query()
        return self.table.contains((query.identifier == identifier) & (query.node_identifier == node_identifier))
