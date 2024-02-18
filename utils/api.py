from functools import wraps

import jwt
from flask import g, request


def required_param(key: str, data_type=str):
    if not g.request_body:
        raise Exception("Request body is missing")
    if key not in g.request_body:
        raise Exception(f"{key} is required")
    val = g.request_body[key]
    if not isinstance(val, data_type):
        raise Exception(f"Invalid data type for value of {key}")
    return val


def optional_param(key: str, data_type=str):
    if not g.request_body:
        return None
    if key not in g.request_body:
        return None
    val = g.request_body[key]
    if not isinstance(val, data_type):
        raise Exception(f"Invalid data type for value of {key}")
    return val


def page():
    return request.args.get("page", 0, int)


def size():
    return request.args.get("size", 50, int)


def authenticate_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise Exception("Invalid access token")

        try:
            data = jwt.decode(token, g.jwt_signing_key, algorithms=['HS256'], issuer=g.vertex, audience=g.vertex)

            if data["type"] != "admin":
                raise Exception("Invalid access token")

            current_admin = {
                "username": data["sub"]
            }
        except Exception as _:
            raise Exception("Invalid access token")

        return f(current_admin, *args, **kwargs)

    return decorated


def resolve_kid(kid: str):
    components = kid.split("/")

    if len(components) != 2:
        pass

    vertex = components[0]
    node = components[1]

    if vertex == g.vertex:
        public_key = g.node_service.get_signing_public_key(node)
        return {
            "public_key": public_key,
            "node_identifier": node,
            "vertex": vertex
        }
    else:
        raise Exception("Remote node authentication not implemented")


def authenticate_actor(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise Exception("Invalid access token")

        try:
            headers = jwt.get_unverified_header(token)

            if "kid" not in headers:
                raise Exception("Invalid access token")

            parsed_kid = resolve_kid(headers["kid"])

            public_key = parsed_kid["public_key"]
            source_node_identifier = parsed_kid["node_identifier"]
            source_vertex = parsed_kid["vertex"]

            data = jwt.decode(
                token,
                key=public_key,
                algorithms=['EdDSA'],
                issuer=f"{source_vertex}/{source_node_identifier}",
                audience=f"{g.vertex}/{kwargs['node_identifier']}",
            )

            if data["type"] != "actor":
                raise Exception("Invalid access token")

            current_actor = {
                "identifier": data["sub"],
                "node_identifier": source_node_identifier,
                "vertex": source_vertex,
                "node_address": f"{source_vertex}/{source_node_identifier}"
            }
        except Exception as _:
            raise Exception("Invalid access token")

        return f(current_actor, *args, **kwargs)

    return decorated
