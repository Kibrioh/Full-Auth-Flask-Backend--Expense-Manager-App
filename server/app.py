import os
from flask import Flask
from flask_migrate import Migrate

from models import db, bcrypt          # bcrypt is new
from expenses import expenses_bp
from auth import auth_bp               # new

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(expenses_bp)
app.register_blueprint(auth_bp)


if __name__ == '__main__':
    app.run(port=5555, debug=True)