from flask import Flask
from .admin_manager import AdminManager
from utils.api import *


class AdminApi:
    def __init__(self, app: Flask, manager: AdminManager) -> None:
        self.app = app
        self.manager = manager

    def register(self):
        @self.app.post("/api/v1/admins/initialize")
        def initialize_admin():
            return self.manager.initialize(
                required_param("username"),
                required_param("password")
            )

        @self.app.post("/api/v1/admins/token")
        def get_admin_token():
            return self.manager.get_token(
                required_param("username"),
                required_param("password")
            )
