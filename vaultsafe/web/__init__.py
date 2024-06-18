# vaultsafe/web/__init__.py
from flask import Flask

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Import routes
    from vaultsafe.web.routes import bp
    app.register_blueprint(bp)
    
    return app

