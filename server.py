from flask import Flask, request, g
from dotenv import load_dotenv
import os
from admin.admin_manager import AdminManager
from health.health_api import HealthApi
from admin.admin_api import AdminApi
from tinydb import TinyDB

load_dotenv()

jwt_signing_key = os.getenv("JWT_SIGNING_KEY")
vertex = os.getenv("VERTEX")
vertex_description = os.getenv("VERTEX_DESCRIPTION")
data_path = os.getenv("DATA_PATH")
if not os.path.exists(data_path):
    os.makedirs(data_path)

app = Flask(__name__)
db = TinyDB(os.path.join(data_path, "vertex.json"))

admin_manager = AdminManager(db.table("admins"), vertex, jwt_signing_key)

HealthApi(app, vertex_description).register()
AdminApi(app, admin_manager).register()

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
