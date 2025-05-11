from flask import Blueprint

billing_bp = Blueprint('billing', __name__, url_prefix='/admin/billing')

from . import routes_get
from . import routes_post
from . import routes_put
from . import routes_delete
