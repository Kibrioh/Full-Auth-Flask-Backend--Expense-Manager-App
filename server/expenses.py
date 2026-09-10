from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db, Resource, User

expenses_bp = Blueprint("expenses", __name__)


def get_current_user():
    """
    TODO: replace with real JWT/session auth once merged.
    Must return the logged-in User object (or None).
    """
    return User.query.get(1)  # placeholder: seeded demo user


def resource_to_dict(r):
    return {
        "id": r.id,
        "title": r.title,
        "amount": float(r.amount),
        "category": r.category,
        "expense_date": r.expense_date.isoformat(),
        "notes": r.notes,
        "created_at": r.created_at.isoformat(),
        "user_id": r.user_id,
    }


@expenses_bp.route("/expenses", methods=["GET"])
def get_expenses():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Resource.query.filter_by(user_id=user.id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "expenses": [resource_to_dict(r) for r in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }), 200


@expenses_bp.route("/expenses", methods=["POST"])
def create_expense():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    required = ["title", "amount", "category", "expense_date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        expense_date = datetime.strptime(data["expense_date"], "%Y-%m-%d").date()
        amount = float(data["amount"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount or expense_date (expected YYYY-MM-DD)"}), 400

    expense = Resource(
        title=data["title"],
        amount=amount,
        category=data["category"],
        expense_date=expense_date,
        notes=data.get("notes"),
        user_id=user.id,
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(resource_to_dict(expense)), 201


@expenses_bp.route("/expenses/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    expense = Resource.query.get(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    if expense.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    if "title" in data:
        expense.title = data["title"]
    if "category" in data:
        expense.category = data["category"]
    if "notes" in data:
        expense.notes = data["notes"]
    if "amount" in data:
        try:
            expense.amount = float(data["amount"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400
    if "expense_date" in data:
        try:
            expense.expense_date = datetime.strptime(data["expense_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid expense_date (expected YYYY-MM-DD)"}), 400

    db.session.commit()
    return jsonify(resource_to_dict(expense)), 200


@expenses_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    expense = Resource.query.get(expense_id)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404
    if expense.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(expense)
    db.session.commit()
    return "", 204