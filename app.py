import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db
from routes.main import main_bp
from routes.donor import donor_bp
from routes.request import request_bp
from routes.admin import admin_bp
from utils.seed import seed_database

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(admin_bp)

    # Register Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Initialize database tables and sample data
    with app.app_context():
        db.create_all()
        seed_database()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
