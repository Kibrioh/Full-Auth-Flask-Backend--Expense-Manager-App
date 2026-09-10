from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()


class User(db.Model):
    """An account that owns expense resources."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    _password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    resources = db.relationship(
        "Resource",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @hybrid_property
    def password_hash(self):
        # Write-only: never expose the stored hash.
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, plaintext_password):
        hashed = bcrypt.generate_password_hash(plaintext_password.encode("utf-8"))
        self._password_hash = hashed.decode("utf-8")

    def authenticate(self, plaintext_password):
        """Return True if the plaintext matches the stored hash."""
        return bcrypt.check_password_hash(
            self._password_hash, plaintext_password.encode("utf-8")
        )

    def to_dict(self):
        """Safe user representation for API responses (no password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.username}>"


class Resource(db.Model):
    """An expense record belonging to one user."""

    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user = db.relationship("User", back_populates="resources")

    def __repr__(self):
        return f"<Resource {self.title}>"