from flask import Flask, request, g
from dotenv import load_dotenv
import os
from health.health_api import HealthApi

load_dotenv()

app = Flask(__name__)
jwt_signing_key = os.getenv("JWT_SIGNING_KEY")
vertex = os.getenv("VERTEX")
vertex_description = os.getenv("VERTEX_DESCRIPTION")

HealthApi(app, vertex_description).register()

@app.before_request
def before_request():
    g.request_body = request.get_json(force=True, silent=True)
    g.jwt_signing_key = jwt_signing_key
    g.vertex = vertex


@app.errorhandler(404)
def handle_404_error(e):
    return {
        "success": False,
        "message": str(e)
    }, 404


@app.errorhandler(Exception)
def handle_all_errors(e):
    return {
        "success": False,
        "message": str(e)
    }, 500

def main():
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")), debug=os.getenv("DEBUG") == "true")

if __name__ == "__main__":
    main()
