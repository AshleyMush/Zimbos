from flask import Blueprint

main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../../templates/main',
    static_folder='static',

)
from . import routes  # Import routes after creating the blueprint