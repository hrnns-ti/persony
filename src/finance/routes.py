from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.db import get_connection

bp = Blueprint("finance", __name__, url_prefix="/api/finance")


# GET /api/finance/transactions - List transactions user
@bp.get("/transactions")
@jwt_required()
def get_transactions():
    user_id = int(get_jwt_identity())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ID, AMOUNT, TYPE, CATEGORY, DESCRIPTION, TRANSACTION_DATE
                FROM FINANCE_TRANSACTIONS 
                WHERE USER_ID = :user_id
                ORDER BY TRANSACTION_DATE DESC
            """, {"user_id": user_id})

            columns = [col[0] for col in cur.description]
            transactions = [dict(zip(columns, row)) for row in cur.fetchall()]

    return jsonify(transactions)


# POST /api/finance/transactions - Create transaction
@bp.post("/transactions")
@jwt_required()
def create_transaction():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ['amount', 'type', 'category', 'transaction_date']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO FINANCE_TRANSACTIONS 
                (USER_ID, AMOUNT, TYPE, CATEGORY, DESCRIPTION, TRANSACTION_DATE)
                VALUES (:user_id, :amount, :type, :category, :description, TO_DATE(:transaction_date, 'YYYY-MM-DD'))
                RETURNING ID
            """, {
                "user_id": user_id,
                "amount": data['amount'],
                "type": data['type'],
                "category": data['category'],
                "description": data.get('description', ''),
                "transaction_date": data['transaction_date']
            })

            transaction_id = cur.fetchone()[0]
            conn.commit()

    return jsonify({"id": transaction_id, "message": "Transaction created"}), 201


# GET /api/finance/summary - Balance summary
@bp.get("/summary")
@jwt_required()
def get_summary():
    user_id = int(get_jwt_identity())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN TYPE='INCOME' THEN AMOUNT ELSE 0 END) as income,
                    SUM(CASE WHEN TYPE='EXPENSE' THEN AMOUNT ELSE 0 END) as expense,
                    SUM(CASE WHEN TYPE='INCOME' THEN AMOUNT ELSE -AMOUNT END) as balance
                FROM FINANCE_TRANSACTIONS 
                WHERE USER_ID = :user_id
            """, {"user_id": user_id})

            columns = [col[0] for col in cur.description]
            summary = dict(zip(columns, cur.fetchone()))

    return jsonify(summary)
