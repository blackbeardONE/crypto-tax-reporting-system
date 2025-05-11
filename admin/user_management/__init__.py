from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import routes_get
from . import routes_post
from . import routes_put
from . import routes_delete
