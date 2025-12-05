import os
from flask import Flask
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)

    from src.common.routes import bp as common_bp
    from src.user import bp as user_bp
    from src.calendar import bp as calendar_bp
    from src.finance import bp as finance_bp

    app.register_blueprint(common_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(finance_bp)

    return app