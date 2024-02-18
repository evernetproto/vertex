from flask import Flask, g


class HealthApi:
    def __init__(self, app: Flask, vertex_description: str) -> None:
        self.app = app
        self.vertex_description = vertex_description

    def register(self):
        
        @self.app.get("/health")
        def health_check():
            return {
                "success": True
            }
    
        @self.app.get("/info")
        def vertex_info():
            return {
                "vertex": g.vertex,
                "description": self.vertex_description
            }
