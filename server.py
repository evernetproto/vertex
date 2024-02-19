import traceback
from flask import Flask, request, g
from dotenv import load_dotenv
import os
from tinydb import TinyDB

from admin.admin_manager import AdminManager
from node.node_manager import NodeManager
from actor.actor_manager import ActorManager

from health.health_api import HealthApi
from admin.admin_api import AdminApi
from node.node_api import NodeApi
from actor.actor_api import ActorApi


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
node_manager = NodeManager(db.table("nodes"))
actor_manager = ActorManager(db.table("actors"), node_manager, vertex)

HealthApi(app, vertex_description).register()
AdminApi(app, admin_manager).register()
NodeApi(app, node_manager).register()
ActorApi(app, actor_manager).register()

@app.before_request
def before_request():
    g.request_body = request.get_json(force=True, silent=True)
    g.jwt_signing_key = jwt_signing_key
    g.vertex = vertex
    g.node_manager = node_manager


@app.errorhandler(404)
def handle_404_error(e):
    return {
        "success": False,
        "message": str(e)
    }, 404


@app.errorhandler(Exception)
def handle_all_errors(e):
    print(traceback.format_exc())
    return {
        "success": False,
        "message": str(e)
    }, 500

def main():
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")), debug=os.getenv("DEBUG") == "true")

if __name__ == "__main__":
    main()
