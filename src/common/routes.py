from flask import Blueprint
from src.db import get_connection

bp = Blueprint('api', __name__)

@bp.get('/health')
def health():
    return {"status": "OK 🚀"}

@bp.get('/db-ping')
def db_ping():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 'OK' FROM dual")
            (val,) = cur.fetchone()
    return { "database": val }

