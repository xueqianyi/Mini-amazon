from flask import render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length, InputRequired

from .models.product import Product
from .models.user import User
from .models.feedback import FeedbackToProduct

from .models.cart import Cart
from .models.user import User

import base64
import os
from .models.order import Order

from flask import Blueprint
bp = Blueprint('products', __name__)

@bp.route('/products')
def show_products():
    k = request.args.get('k', default='', type=str)
    s = request.args.get('s', default='relevanceblender', type=str)
    category = request.args.get('category', default='All', type=str)
    items = Product.search_and_sort(k, s, category)
    return render_template('items.html', items=items)


class FeedbackForm(FlaskForm):
    score = DecimalField('Score', validators=[InputRequired(), NumberRange(min=0, max=5)], places=2)
    content = TextAreaField('Content', validators=[InputRequired(), Length(max=3000)])
    image = StringField('Image')
    submit = SubmitField('Submit')

# @bp.route('/product/<int:sellerId>/<int:productId>', methods=['GET'])
# def show_detailed_product(sellerId, productId):
#     k = request.args.get('k', default='', type=str)
#     category = request.args.get('category', default='All', type=str)

#     form = FeedbackForm()
#     Product.update_avg_review_rating(sellerId, productId)
#     product = Product.get_product_by_sid_pid(sellerId, productId)
#     similar_products = Product.search_and_sort(k, 'relevanceblender', category, 3, sellerId, productId)
#     if len(similar_products) < 3:
#         quantity = 3 - len(similar_products)
#         less_similar_products = Product.search_and_sort(k, 'relevanceblender', 'All', quantity, sellerId, productId)
#         for product in less_similar_products:
#             similar_products.append(product)
#     seller = User.get_by_uid(sellerId)
#     feedbacks = FeedbackToProduct.get_by_product(productId, sellerId)
    
#     showMyFeedback = False
#     if current_user.is_authenticated and Order.have_bought_seller(current_user.id, sellerId) != 0:
#         showMyFeedback = True
#         # find the feedback of the current user
#         for feedback in feedbacks:
#             if feedback.uid == current_user.id:
#                 if feedback.image:
#                     image_base64 = feedback.image
#                 else:
#                     image_base64 = None
#                 form = FeedbackForm(score=feedback.score, content=feedback.content, image=image_base64)
#                 break

#     return render_template('detailed_product.html', form=form, seller=seller, product=product, similar_products=similar_products, feedbacks=feedbacks, showMyFeedback=showMyFeedback)
@bp.route('/product/<int:sellerId>/<int:productId>', methods=['GET'])
def show_detailed_product(sellerId, productId):
    k = request.args.get('k', default='', type=str)
    category = request.args.get('category', default='All', type=str)

    form = FeedbackForm()
    Product.update_avg_review_rating(sellerId, productId)
    product = Product.get_product_by_sid_pid(sellerId, productId)
    similar_products = Product.get_similar_products(productId)
    # if len(similar_products) < 3:
    #     quantity = 3 - len(similar_products)
    #     less_similar_products = Product.search_and_sort(k, 'relevanceblender', 'All', quantity, sellerId, productId)
    #     for product in less_similar_products:
    #         similar_products.append(product)
    seller = User.get_by_uid(sellerId)
    feedbacks = FeedbackToProduct.get_by_product(productId, sellerId)

    showMyFeedback = False
    if current_user.is_authenticated and Order.have_bought_seller(current_user.id, sellerId) != 0:
        showMyFeedback = True
        # find the feedback of the current user
        for feedback in feedbacks:
            if feedback.uid == current_user.id:
                if feedback.image:
                    image_base64 = feedback.image
                else:
                    image_base64 = None
                form = FeedbackForm(score=feedback.score, content=feedback.content, image=image_base64)
                break

    return render_template('detailed_product.html', form=form, seller=seller, product=product, similar_products=similar_products, feedbacks=feedbacks, showMyFeedback=showMyFeedback)

@bp.route('/items/<int:sellerId>/<int:productId>/feedbackSubmit', methods=['POST'])
def review_submit(sellerId, productId):
    form = FeedbackForm()
    if form.validate_on_submit():
        product = Product.get_product_by_sid_pid(sellerId, productId)
        if product is None:
            return jsonify({"error": "Invalid product"}), 400
        if not current_user.is_authenticated:
            return jsonify({"error": "You are not authorized to submit feedback"}), 401
        
        image = None
        if form.image.data:
            image = form.image.data
        
        if not FeedbackToProduct.insert_or_update(productId, sellerId, current_user.id, form.content.data, form.score.data, image):
            return jsonify({"error": "Failed to submit feedback"}), 500
        return jsonify({"message": "Feedback submitted successfully"}), 200
    else:
        print(form.errors)
        return jsonify({"error": "Invalid form data"}), 400
    
@bp.route('/items/<int:sellerId>/<int:productId>/feedbackDelete', methods=['DELETE'])
def review_delete(sellerId, productId):
    product = Product.get_product_by_sid_pid(sellerId, productId)
    if product is None:
        return jsonify({"error": "Invalid product"}), 400
    if not current_user.is_authenticated:
        return jsonify({"error": "You are not authorized to delete feedback"}), 401
    
    if not FeedbackToProduct.delete(productId, sellerId, current_user.id):
        return jsonify({"error": "Failed to delete feedback"}), 500
    return jsonify({"message": "Feedback deleted successfully"}), 200

@bp.route('/cart/<int:user_id>', methods=['POST'])
def add_to_cart(user_id):
    # Fetch product details from the form data
    userid=user_id
    pid = request.form.get('pid', type=int)
    sid = request.form.get('sid', type=int)
    quantity = request.form.get('quantity', type=int)

    # Ensure the current user is authenticated and the user_id from the URL matches the current user's ID
    if not current_user.is_authenticated or current_user.id != user_id:
        return redirect(url_for('auth.login'))

    # Add item to cart
    Cart.add_to_cart(user_id, pid, sid, quantity)
    cart_items = Cart.get(user_id)
    return update_cart_view(cart_items,userid)

def update_cart_view(cart_items,user_id):
    user = User.get_by_uid(user_id)
    cart_found = any(not cart.c_status for cart in cart_items)
    saved_found = any(cart.c_status for cart in cart_items)
    cart_total_price = sum(cart.total_price for cart in cart_items if not cart.c_status)

    return render_template('carts.html', user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,cart_total_price=cart_total_price,
    inventory_alert=False,balance_alert=False,coupon_alert=False,flag=0,discount=0)


# @bp.route('/add_to_cart/<int:user_id>/<int:pid>/<int:sid>/<int:quantity>',methods=['POST'])
# def add_to_cart(user_id,pid,sid,quantity): 
#     user = User.get_by_uid(user_id)
#     Cart.add_to_cart(user_id,pid,sid,quantity)
#     if current_user.is_authenticated and current_user.id == user_id:
#         cart_items = Cart.get(current_user.id)
#     else:
#         # Handle unauthenticated users
#         cart_items = []
#     cart_found  = any(not cart.c_status for cart in cart_items)
#     saved_found = any( cart.c_status for cart in cart_items)
#     cart_total_price=0
#     for cart in cart_items:
#         if cart.c_status==False:
#             cart_total_price += cart.total_price
#     return render_template('carts.html', user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,cart_total_price=cart_total_price,
#     inventory_alert=False,balance_alert=False,coupon_alert=False,flag=0,discount=0)



@bp.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if not current_user.is_authenticated or not current_user.isSeller:
        return redirect(url_for('users.login'))  # Ensure only sellers can update products

    new_price = request.form.get('price')
    new_stock = request.form.get('stock')
    new_description = request.form.get('description')
    new_image = request.files.get('image')
    if new_stock is not None and new_stock.isdigit():
        new_stock = int(new_stock)
        # Call the function to update the stock in the database
        Product.update_stock(product_id, new_stock, current_user.id)
        # flash('Stock updated successfully!')
    if new_description is not None:
        Product.update_description(product_id, new_description, current_user.id)
        # flash('Description updated successfully!')
    if new_price is not None:
        Product.update_price(product_id, new_price, current_user.id)
        # flash('Price updated successfully!')
    if new_image and allowed_file(new_image.filename):
        _, ext = os.path.splitext(new_image.filename)
        mime_type = "image/" + ext.lower().strip('.')
        
        # Read the image file and encode it in base64
        image_data = new_image.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        image_data_uri = f"data:{mime_type};base64,{encoded_image}"

        # Save the formatted base64 string to the database
        Product.update_image(product_id, image_data_uri, current_user.id)
        # flash('Image updated successfully!')
    return redirect(url_for('users.edit_products'))

def allowed_file(filename):
    # Check the file extension to ensure it's an image
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    if not current_user.is_authenticated or not current_user.isSeller:
        return redirect(url_for('users.login'))  # Ensure only sellers can update products

    Product.remove_product(product_id, current_user.id)

    return redirect(url_for('users.edit_products'))

@bp.route('/add_product', methods=['POST'])
def add_product():
    if not current_user.is_authenticated or not current_user.isSeller:
        return redirect(url_for('users.login'))  # Ensure only sellers can update products

    product_id = request.form.get('product_id')
    price = request.form.get('price')
    stock = request.form.get('stock')
    Product.insert_productseller_to_current_productseller(current_user.id, product_id, price, stock)
    return redirect(url_for('users.edit_products'))

@bp.route('/create_product', methods=['POST'])
def create_product():
    if not current_user.is_authenticated or not current_user.isSeller:
        return redirect(url_for('users.login'))
    
    category = request.form.get('category')
    name = request.form.get('name')
    Product.insert_new_product(category, name)
    return redirect(url_for('users.edit_products'))