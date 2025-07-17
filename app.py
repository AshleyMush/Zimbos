from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from views.auth.routes import auth_bp
from views.main.routes import main_bp
from views.admin.routes import admin_bp
from models import User
from models import db
from flask_migrate import Migrate, upgrade
from forms import CSRFProtectForm


csrf = CSRFProtect()




def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    csrf.init_app(app)

    # Inject csrf_form into every template
    @app.context_processor
    def inject_csrf_form():
        return {'csrf_form': CSRFProtectForm()}



    # Initialize database
    db.init_app(app)
    with app.app_context():
        # Create tables if not exist
        db.create_all()

    # Initialize migrations
    migrate = Migrate(app, db)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Load user for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))



    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Error Handler for 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app





if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8003)