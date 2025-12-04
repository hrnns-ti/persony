from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.db import get_connection

bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")


@bp.get("/events")
@jwt_required()
def get_events():
    user_id = get_jwt_identity()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ID, TITLE, DESCRIPTION, START_AT, END_AT, IS_ALL_DAY, LOCATION, COLOR
                FROM CALENDAR_EVENTS 
                WHERE USER_ID = :user_id
                ORDER BY START_AT
                """,
                {"user_id": user_id}
            )
            rows = cur.fetchall()

    events = []
    for row in rows:
        events.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "start_at": row[3].isoformat() if row[3] else None,
            "end_at": row[4].isoformat() if row[4] else None,
            "is_all_day": bool(row[5]),
            "location": row[6],
            "color": row[7],
        })

    return jsonify(events)


@bp.post("/events")
@jwt_required()
def create_event():
    data = request.get_json(silent=True) or {}

    user_id = int(get_jwt_identity())

    title = (data.get("title") or "").strip()
    description = data.get("description", "").strip()
    start_at_str = data.get("start_at")
    end_at_str = data.get("end_at")
    is_all_day = data.get("is_all_day", False)
    location = (data.get("location") or "").strip()
    color = data.get("color", "").strip()

    errors = {}
    if not title:
        errors["title"] = "Title is required"
    if not start_at_str:
        errors["start_at"] = "Start time is required"
    if not end_at_str:
        errors["end_at"] = "End time is required"
    if errors:
        return jsonify({"errors": errors}), 400

    # Parse datetime (ISO format)
    try:
        from datetime import datetime
        start_at = datetime.fromisoformat(start_at_str.replace('Z', '+00:00'))
        end_at = datetime.fromisoformat(end_at_str.replace('Z', '+00:00'))
    except ValueError as e:
        return jsonify({"errors": {"datetime": "Invalid date format (use ISO 8601)"}}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            id_var = cur.var(int)

            cur.execute(
                """
                INSERT INTO CALENDAR_EVENTS (
                    USER_ID, TITLE, DESCRIPTION, START_AT, END_AT, 
                    IS_ALL_DAY, LOCATION, COLOR
                )
                VALUES (
                    :user_id, :title, :description, :start_at, :end_at,
                    :is_all_day, :location, :color
                )
                RETURNING ID INTO :id
                """,
                {
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "start_at": start_at,
                    "end_at": end_at,
                    "is_all_day": 1 if is_all_day else 0,
                    "location": location,
                    "color": color,
                    "id": id_var,
                },
            )

            event_id = id_var.getvalue()[0]
        conn.commit()

    return (
        jsonify({"id": event_id, "message": "Event created successfully"}),
        201,
    )


@bp.put("/events/<int:event_id>")
@jwt_required()
def update_event(event_id):
    data = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())

    title = (data.get("title") or "").strip()
    description = data.get("description", "").strip()
    start_at_str = data.get("start_at")
    end_at_str = data.get("end_at")
    is_all_day = data.get("is_all_day", False)
    location = (data.get("location") or "").strip()
    color = data.get("color", "").strip()

    errors = {}
    if not title:
        errors["title"] = "Title is required"
    if not start_at_str:
        errors["start_at"] = "Start time is required"
    if not end_at_str:
        errors["end_at"] = "End time is required"
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        from datetime import datetime
        start_at = datetime.fromisoformat(start_at_str.replace('Z', '+00:00'))
        end_at = datetime.fromisoformat(end_at_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"errors": {"datetime": "Invalid ISO 8601 format"}}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            id_var = cur.var(int)

            cur.execute(
                """
                UPDATE CALENDAR_EVENTS 
                SET TITLE = :title, DESCRIPTION = :description,
                    START_AT = :start_at, END_AT = :end_at,
                    IS_ALL_DAY = :is_all_day, LOCATION = :location, 
                    COLOR = :color, UPDATED_AT = SYSTIMESTAMP
                WHERE ID = :event_id AND USER_ID = :user_id
                RETURNING ID INTO :id
                """,
                {
                    "title": title,
                    "description": description,
                    "start_at": start_at,
                    "end_at": end_at,
                    "is_all_day": 1 if is_all_day else 0,
                    "location": location,
                    "color": color,
                    "event_id": event_id,
                    "user_id": user_id,
                    "id": id_var,
                },
            )

            if cur.rowcount == 0:
                return jsonify({"error": "Event not found or access denied"}), 404

            updated_id = id_var.getvalue()[0]
        conn.commit()

    return jsonify({
        "id": updated_id,
        "message": "Event updated successfully"
    })


@bp.delete("/events/<int:event_id>")
@jwt_required()
def delete_event(event_id):
    user_id = int(get_jwt_identity())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM CALENDAR_EVENTS WHERE ID = :event_id AND USER_ID = :user_id",
                {"event_id": event_id, "user_id": user_id}
            )

            if cur.rowcount == 0:
                return jsonify({"error": "Event not found or access denied"}), 404
        conn.commit()

    return jsonify({"message": "Event deleted successfully"})