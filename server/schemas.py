from marshmallow import Schema, fields, validate


class ExpenseSchema(Schema):
    """Schema for validating, deserializing, and serializing expenses."""

    id = fields.Integer(dump_only=True)

    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=120)
    )

    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0)
    )

    category = fields.String(
        required=True,
        validate=validate.Length(min=1, max=80)
    )

    expense_date = fields.Date(required=True)

    notes = fields.String(
        allow_none=True,
        required=False
    )

    created_at = fields.DateTime(dump_only=True)

    user_id = fields.Integer(dump_only=True)
