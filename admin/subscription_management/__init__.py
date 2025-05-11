from flask import Blueprint

subscription_bp = Blueprint('subscription', __name__, url_prefix='/admin/subscription')

from . import routes_get
from . import routes_post
from . import routes_put
from . import routes_delete
