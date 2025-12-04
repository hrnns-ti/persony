from flask import Blueprint, request, jsonify
import oracledb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.db import get_connection

bp = Blueprint("user", __name__, url_prefix="/api/users")

@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip()
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    errors = {}
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"
    if not confirm_password:
        errors["confirm_password"] = "Confirm Password is required"
    if password and confirm_password and password != confirm_password:
        errors["password"] = "Passwords don't match"
    if errors:
        return jsonify({"errors": errors}), 400

    password_hash = generate_password_hash(password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            id_var = cursor.var(int)
            created_at_var = cursor.var(oracledb.DATETIME)

            cursor.execute("""INSERT INTO USERS (EMAIL, PASSWORD_HASH, NAME) VALUES (:email, :password_hash, :name) RETURNING ID, CREATED_AT INTO :id, :created_at""",
                {
                    "email": email,
                    "password_hash": password_hash,
                    "name": name,
                    "id": id_var,
                    "created_at": created_at_var,
                }
            )

            user_id = id_var.getvalue()[0]
            created_at = created_at_var.getvalue()[0]

        connection.commit()

    return (
        jsonify(
            {
                "id": user_id,
                "email": email,
                "name": name,
                "created_at": created_at.isoformat() if created_at else None,
            }
        ),
        201,
    )


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip()  # pakai email!
    password = data.get("password") or ""

    errors = {}
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"
    if errors:
        return jsonify({"errors": errors}), 400

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ID, EMAIL, NAME, PASSWORD_HASH FROM USERS WHERE EMAIL = :email",
                {"email": email}
            )
            row = cursor.fetchone()

            if not row:
                return jsonify({"errors": {"email": "Invalid credentials"}}), 401

            user_id, email, name, password_hash = row

            if not check_password_hash(password_hash, password):
                return jsonify({"errors": {"email": "Invalid credentials"}}), 401

            access_token = create_access_token(identity = str(user_id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user_id,
            "email": email,
            "name": name,
        }
    })
