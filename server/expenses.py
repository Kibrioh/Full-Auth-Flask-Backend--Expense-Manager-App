from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db, Resource, User
from schemas import ExpenseSchema

expenses_bp = Blueprint("expenses", __name__)


def get_current_user():
    """
    TODO: replace with real session authentication once merged.
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
        page=page,
        per_page=per_page,
        error_out=False
    )

    schema = ExpenseSchema(many=True)

    return jsonify({
        "expenses": schema.dump(pagination.items),
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

    schema = ExpenseSchema()

    try:
        data = schema.load(data)
    except Exception as err:
        return jsonify({"errors": err.messages}), 400

    expense = Resource(
        title=data["title"],
        amount=data["amount"],
        category=data["category"],
        expense_date=data["expense_date"],
        notes=data.get("notes"),
        user_id=user.id,
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify(schema.dump(expense)), 201


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

    schema = ExpenseSchema()

    try:
        validated_data = schema.load(data, partial=True)
    except Exception as err:
        return jsonify({"errors": err.messages}), 400

    for field in ["title", "amount", "category", "expense_date", "notes"]:
        if field in validated_data:
            setattr(expense, field, validated_data[field])

    db.session.commit()

    return jsonify(schema.dump(expense)), 200


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
