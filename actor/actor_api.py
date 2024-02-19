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
