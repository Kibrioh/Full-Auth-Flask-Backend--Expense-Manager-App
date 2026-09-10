from flask import Flask
from flask_migrate import Migrate

from models import db
from expenses import expenses_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
app.register_blueprint(expenses_bp)
db.init_app(app)



if __name__ == '__main__':
    app.run(port=5555, debug=True)