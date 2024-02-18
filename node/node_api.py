from flask import Flask
from .node_manager import NodeManager
from utils.api import *


class NodeApi:
    def __init__(self, app: Flask, manager: NodeManager) -> None:
        self.app = app
        self.manager = manager

    def register(self):
        
        @self.app.post("/api/v1/nodes")
        @authenticate_admin
        def create_node(admin):
            return self.manager.create(
                required_param("identifier"),
                required_param("display_name"),
                optional_param("description"),
                required_param("actor_sign_up_enabled", bool),
                admin["username"]
            )

        @self.app.get("/api/v1/nodes")
        def list_nodes():
            return self.manager.list()

        @self.app.get("/api/v1/nodes/<identifier>")
        def get_node(identifier):
            return self.manager.get(identifier)

        @self.app.put("/api/v1/nodes/<identifier>")
        @authenticate_admin
        def update_node(_, identifier):
            return self.manager.update(identifier,
                                       optional_param("display_name"),
                                       optional_param("description"))
