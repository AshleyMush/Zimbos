from flask import Blueprint

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='../../templates/admin',
    static_folder='static',
    url_prefix='/admin'

)

from . import routes  # Import routes after creating the blueprint