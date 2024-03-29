from flask import Flask
from .actor_manager import ActorManager
from utils.api import *


class ActorApi:
    def __init__(self, app: Flask, manager: ActorManager) -> None:
        self.app = app
        self.manager = manager

    def register(self):
        
        @self.app.post("/api/v1/nodes/<node_identifier>/actors/signup")
        def sign_up_actor(node_identifier):
            return self.manager.sign_up(
                node_identifier,
                required_param("identifier"),
                required_param("password"),
                required_param("type"),
                required_param("display_name"),
                optional_param("description")
            )

        @self.app.post("/api/v1/nodes/<node_identifier>/actors/token")
        def get_actor_token(node_identifier):
            return self.manager.get_token(
                required_param("identifier"),
                required_param("password"),
                node_identifier,
                optional_param("target_node_address")
            )
    
        @self.app.get("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def get_current_actor_details(actor, node_identifier):
            validate_actor_is_local(actor, node_identifier)
            return self.manager.get(actor["identifier"], node_identifier)

        @self.app.put("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def update_current_actor(actor, node_identifier):
            validate_actor_is_local(actor, node_identifier)
            return self.manager.update(actor["identifier"],
                                       optional_param("display_name"),
                                       optional_param("description"),
                                       optional_param("type"),
                                       node_identifier)
        
        @self.app.put("/api/v1/nodes/<node_identifier>/actors/current/password")
        @authenticate_actor
        def change_current_actor_password(actor, node_identifier):
            validate_actor_is_local(actor, node_identifier)
            return self.manager.change_password(actor["identifier"],
                                                required_param("password"),
                                                node_identifier)

        @self.app.delete("/api/v1/nodes/<node_identifier>/actors/current")
        @authenticate_actor
        def delete_current_actor(actor, node_identifier):
            validate_actor_is_local(actor, node_identifier)
            return self.manager.delete(actor["identifier"], node_identifier)

        @self.app.post("/api/v1/nodes/<node_identifier>/actors")
        @authenticate_admin
        def add_actor(admin, node_identifier):
            return self.manager.add(node_identifier,
                                    required_param("identifier"),
                                    required_param("type"),
                                    required_param("display_name"),
                                    optional_param("description"),
                                    admin["username"])

        @self.app.delete("/api/v1/nodes/<node_identifier>/actors/<identifier>")
        @authenticate_admin
        def delete_actor(_, node_identifier, identifier):
            return self.manager.delete(identifier, node_identifier)

        @self.app.put("/api/v1/nodes/<node_identifier>/actors/<identifier>/password")
        @authenticate_admin
        def reset_actor_password(_, node_identifier, identifier):
            return self.manager.reset_password(identifier, node_identifier)
        
        @self.app.put("/api/v1/nodes/<node_identifier>/actors/<identifier>")
        @authenticate_admin
        def update_actor(_, node_identifier, identifier):
            return self.manager.update(identifier,
                                       optional_param("display_name"),
                                       optional_param("description"),
                                       optional_param("type"),
                                       node_identifier)
