
from flask import jsonify, redirect, render_template, url_for

from flask import Blueprint
from flask_login import current_user

from app.models.analytics.buyer_seller import Buyer_seller
from app.models.orderhistory import Orderhistory

bp = Blueprint('sellers', __name__)

@bp.route('/sellers/orderhistory')
def orderhistory(): 
    if not current_user.isSeller:
        return redirect(url_for('users.login'))
    if current_user.is_authenticated and current_user.isSeller:
        orderhistorys = Orderhistory.get(current_user.id)
        grouped_data = {}
        for item in orderhistorys:
            key = item.orderkey
            # Append the item to the list for the corresponding 'orderkey'
            if key in grouped_data:
                grouped_data[key].append(item)
            else:
                grouped_data[key] = [item]

    return render_template('seller_orders.html', items = grouped_data)


@bp.route('/sellers/fulfilment/update/<int:orderkey>/<int:pid>/<new_status>', methods=['POST'])
def update_fulfilment(orderkey, pid, new_status):
    Orderhistory.update_fulfilment(orderkey, pid, current_user.id, new_status)
    return jsonify({ 'success': 'ok', 'new_status': new_status }), 200

@bp.route('/sellers/dashboard')
def buyer_to_seller():
    res = Buyer_seller.get_score(current_user.id)
    grouped_data = {}
    for item in res:
        key = item.uid
        # Append the item to the list for the corresponding 'orderkey'
        if key in grouped_data:
            grouped_data[key].append(item)
        else:
            grouped_data[key] = [item]
    return render_template('sellers_dashboard.html', items = grouped_data)