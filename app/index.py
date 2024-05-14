from flask import redirect, render_template, url_for
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    print("-----------------call index-----------------")
    # get all available products for sale:
    if current_user.is_authenticated:
    
        products = Product.get_all()

    else:
        return redirect(url_for('users.login'))

    avail_products = Product.get_products_by_sid(current_user.id)
    return render_template('index.html', avail_products=avail_products)
