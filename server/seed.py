from datetime import date

from app import app
from models import Resource, User, db


with app.app_context():
    Resource.query.delete()
    User.query.delete()

    user1 = User(username="Alice", email="alice@gmail.com", _password_hash="12345678")
    user2 = User(username="Bob", email="bob@gmail.com", _password_hash="12345678")
    user3 = User(username="Carol", email="carol@gmail.com", _password_hash="12345678")

    resources = (
        Resource(
            user=user1,
            title="Monthly groceries",
            amount="82.45",
            category="Food",
            expense_date=date(2026, 1, 5),
            notes="Weekly market run",
        ),
        Resource(
            user=user1,
            title="Internet subscription",
            amount="45.00",
            category="Utilities",
            expense_date=date(2026, 1, 10),
            notes="Home broadband",
        ),
        Resource(
            user=user1,
            title="Bus fare",
            amount="12.00",
            category="Transport",
            expense_date=date(2026, 1, 12),
            notes=None,
        ),
        Resource(
            user=user2,
            title="Gym membership",
            amount="35.00",
            category="Health",
            expense_date=date(2026, 1, 3),
            notes="January membership",
        ),
        Resource(
            user=user2,
            title="Office lunch",
            amount="14.25",
            category="Food",
            expense_date=date(2026, 1, 8),
            notes="Lunch with team",
        ),
        Resource(
            user=user2,
            title="Mobile data",
            amount="20.00",
            category="Utilities",
            expense_date=date(2026, 1, 15),
            notes="Monthly data bundle",
        ),
        Resource(
            user=user3,
            title="Fuel",
            amount="60.00",
            category="Transport",
            expense_date=date(2026, 1, 4),
            notes="Weekly fuel refill",
        ),
        Resource(
            user=user3,
            title="Streaming subscription",
            amount="12.99",
            category="Entertainment",
            expense_date=date(2026, 1, 9),
            notes="Monthly subscription",
        ),
        Resource(
            user=user3,
            title="Books",
            amount="28.50",
            category="Education",
            expense_date=date(2026, 1, 18),
            notes="Programming books",
        ),
    )

    db.session.add_all((user1, user2, user3, *resources))
    db.session.commit()
