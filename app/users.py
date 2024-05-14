import app
from flask import render_template, redirect, url_for, flash, request, jsonify, Flask
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, TextAreaField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, Length, NumberRange

from .models.user import User
from .models.product import Product
from .models.feedback import FeedbackToProduct, FeedbackToSeller
from .models.order import Order
from .models.cart import Cart

import re
from decimal import Decimal, ROUND_UP
from flask import request

from flask import Blueprint
app = Flask(__name__)
bp = Blueprint('users', __name__)

from flask import request, jsonify


### protect from SQL injection
@bp.before_request
def before_request():
    if request.method == 'POST':
        print("detect post requests...................")
        data = {}
        if request.is_json:
            data = request.get_json()  
        else:
            data = request.form 
        print(data)
        for v in data.values():
            v = str(v).lower()

            pattern = r"\b(and|like|exec|insert|select|drop|grant|alter|delete|update|count|chr|mid|master|truncate|char|declare|or)\b|(\*|;)"
            if re.search(pattern, v):  
                flash("Please enter the correct parameters without SQL keywords or special characters.")
                return jsonify({"error": "Please enter the correct parameters without SQL keywords or special characters."}), 400


class FeedbackForm(FlaskForm):
    score = DecimalField('Score', validators=[InputRequired(), NumberRange(min=0, max=5)], places=2)
    content = TextAreaField('Content', validators=[InputRequired(), Length(max=3000)])
    image = StringField('Image')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    balance = FloatField('Balance', validators=[DataRequired()])
    isSeller = BooleanField('Register as a Seller')
    submit = SubmitField('Update')


@bp.route('/user/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        current_user.balance = form.balance.data
        current_user.isSeller = form.isSeller.data

        if User.email_exists(current_user.email):
            flash('Already a user with this email.')
            return render_template('edit_profile.html', form=form)
        User.update_profile(current_user.id, current_user.firstname, current_user.lastname, current_user.email,
                    current_user.address, current_user.balance, current_user.isSeller)
        flash('Your profile has been updated.')
        return redirect(url_for('users.user_detail', user_id=current_user.id))

    return render_template('edit_profile.html', form=form)
    
@bp.route('/user/<int:user_id>', methods=['GET'])
def user_detail(user_id): 
    form = FeedbackForm()
    user = User.get_by_uid(user_id)
    feedbacksByThis = FeedbackToProduct.get_by_user(user_id)
    
    showMyFeedback = False
    if user.isSeller:
        feedbacksByOther = FeedbackToSeller.get_by_seller(user_id)
        avgScore = FeedbackToSeller.get_avg_score(user_id)
        
        if current_user.is_authenticated and current_user.id != user_id and Order.have_bought_seller(current_user.id, user_id) != 0:
            showMyFeedback = True
            
    else:
        feedbacksByOther = None
        avgScore = 0
    
        
    if current_user.is_authenticated:
        if current_user.id == user_id:
            # get orders for a specific user.
            userOrders = Order.get_by_uid(user_id)
        else:
            # find the feedback of the current user
            for feedback in feedbacksByOther:                
                if feedback.uid == current_user.id:
                    if feedback.image:
                        image_base64 = feedback.image
                    else:
                        image_base64 = None
                    form = FeedbackForm(score=feedback.score, content=feedback.content, image=image_base64)
                    break
      
            userOrders = None
    else:
        userOrders = None
    return render_template('user_detail.html', form=form, user=user, orders= userOrders, feedbacksByThis=feedbacksByThis, feedbacksByOther=feedbacksByOther, avgScore=avgScore, showMyFeedback=showMyFeedback)

@bp.route('/user/<int:seller_id>/feedbackSubmit', methods=['POST'])
def review_submit(seller_id):
    form = FeedbackForm()
    if form.validate_on_submit():
        seller = User.get_by_uid(seller_id)
        if seller is None or not seller.isSeller:
            return jsonify({"error": "Invalid Seller"}), 400
        if not current_user.is_authenticated or Order.have_bought_seller(current_user.id, seller_id) == 0:
            return jsonify({"error": "You are not authorized to submit feedback"}), 401
        
        image = None
        if form.image.data:
            image = form.image.data
        
        if not FeedbackToSeller.insert_or_update(seller_id, current_user.id, form.content.data, form.score.data, image):
            return jsonify({"error": "Failed to submit feedback"}), 500
        # Product.update_avg_review_rating(seller_id, product_id)
        return jsonify({"message": "Feedback submitted successfully"}), 200
    else:
        print(form.errors)
        return jsonify({"error": "Invalid form data"}), 400
    
@bp.route('/user/<int:seller_id>/feedbackDelete', methods=['DELETE'])
def review_delete(seller_id):
    seller = User.get_by_uid(seller_id)
    if seller is None or not seller.isSeller:
        return jsonify({"error": "Invalid Seller"}), 400
    if not current_user.is_authenticated:
        return jsonify({"error": "You are not authorized to delete feedback"}), 401
    
    if not FeedbackToSeller.delete(seller_id, current_user.id):
        return jsonify({"error": "Failed to delete feedback"}), 500
    # Product.update_avg_review_rating(seller_id, product_id)
    return jsonify({"message": "Feedback deleted successfully"}), 200



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.isSeller:
            return redirect(url_for('users.seller_page', id=current_user.id))
        else:
            return redirect(url_for('index.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        # print(user)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':  
            if not user.isSeller:
                next_page = url_for('index.index')  
            else:
                next_page = url_for('users.seller_page', id=current_user.id) 

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])  
    isSeller = BooleanField('Register as A Seller')
    submit = SubmitField('Register')
    

    def validate_email(self, email):
        if User.email_exists(email.data):
            flash('Already a user with this email.')
            return redirect(url_for('users.register'))
            # raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data,
                         form.isSeller.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    print("-------------logout----------------")
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/seller_page/<int:id>')
def seller_page(id):
    # brought_products = 0
    print("-------------seller_page----------------")
    avail_products = Product.get_products_by_sid(id)
    return render_template('index.html', avail_products=avail_products)

        
@bp.route('/cart/<int:user_id>')
def user_cart(user_id): 
    user = User.get_by_uid(user_id)
    if current_user.is_authenticated and current_user.id == user_id:
        cart_items = Cart.get(current_user.id)
    else:
        # Handle unauthenticated users
        cart_items = []
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += cart.total_price
    return render_template('carts.html', user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,
     cart_total_price=cart_total_price,inventory_alert=False,balance_alert=False,coupon_alert=False,flag=0,discount=0)

@bp.route('/cart/delete/<int:user_id>/<pid>/<sid>', methods=['GET','POST'])
def delete_item(user_id,pid, sid):
    user = User.get_by_uid(user_id)
    Cart.delete_item(current_user.id, pid, sid)
    cart_items = Cart.get(current_user.id)   
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status== False:
            cart_total_price += cart.total_price
    return render_template('carts.html', user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,
      cart_total_price=cart_total_price,inventory_alert=False,balance_alert=False,coupon_alert=False,flag=0,discount=0)

@bp.route('/cart/sdfl/<int:user_id>/<pid>/<sid>', methods=['GET','POST'])
def save_for_later(user_id,pid, sid):
    user = User.get_by_uid(user_id)
    Cart.save_for_later(current_user.id, pid, sid)
    cart_items = Cart.get(current_user.id)   
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += cart.total_price
    return render_template("carts.html", user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,
     cart_total_price=cart_total_price,inventory_alert=False,balance_alert=False, coupon_alert=False,flag=0,discount=0)

@bp.route('/cart/mdtc/<int:user_id>/<pid>/<sid>', methods=['GET','POST'])
def move_to_cart(user_id,pid, sid):
    user = User.get_by_uid(user_id)
    Cart.move_to_cart(current_user.id, pid, sid)
    cart_items = Cart.get(current_user.id)   
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += cart.total_price
    return render_template("carts.html", user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,
     cart_total_price=cart_total_price,inventory_alert=False,balance_alert=False, coupon_alert=False,flag=0,discount=0)

@bp.route('/cart/cq/<int:user_id>/<pid>/<sid>', methods=['GET','POST'])
def change_quantity(user_id,pid, sid):
    user = User.get_by_uid(user_id)
    new_quantity = request.form.get('quantity', type=int)
    Cart.change_quantity(current_user.id, pid, sid,new_quantity)
    cart_items = Cart.get(current_user.id)   
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += cart.total_price
    return render_template("carts.html", user=user,cart_items=cart_items,cart_found=cart_found,saved_found=saved_found,
     cart_total_price=cart_total_price,inventory_alert=False,balance_alert=False, coupon_alert=False,flag=0,discount=0)


@bp.route('/cart/checkout/<int:user_id>', methods=['GET', 'POST'])


def helper_function(user_id):
    action = request.form.get('action', '')
    code = request.form.get('coupon_code', '')
    if action == 'apply_coupon':
        return apply_coupon(user_id,code)
    else:
       return checkout(user_id,code)

#The coupon code for each user is <user id>+"coupon"+<how much percent off>+"percentoff"
def apply_coupon(user_id,code):
    user = User.get_by_uid(user_id)
    cart_items = Cart.get(current_user.id)   
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += cart.total_price
    cart_total_price = Decimal(cart_total_price)
    pattern = r'^(\d+)coupon([0-4]?[0-9]|50)percentoff$'
    #valid coupon code
    if re.match(pattern, code):
        match=re.match(pattern, code)
        code_user_id = int(match.group(1))  
        discount = int(match.group(2)) 
        if code_user_id == user_id:
            cart_total_price = cart_total_price * (Decimal('1.0') -  Decimal(0.01) * Decimal(discount))
            cart_total_price = cart_total_price.quantize(Decimal('0.01'), rounding=ROUND_UP)
            return render_template(
                "carts.html",
                user=user,
                cart_items=cart_items,
                cart_found=cart_found,
                saved_found=saved_found,
                cart_total_price=cart_total_price,
                inventory_alert=False,
                balance_alert=False,
                coupon_alert=False,
                flag=1,
                discount=discount)
        #This code is valid but not for the current user
        else:
             return render_template(
                "carts.html",
                user=user,
                cart_items=cart_items,
                cart_found=cart_found,
                saved_found=saved_found,
                cart_total_price=cart_total_price,
                inventory_alert=False,
                balance_alert=False,
                coupon_alert=True,
                flag=0,
                discount=0)

    #invalid coupon code
    else:
         return render_template(
                "carts.html",
                user=user,
                cart_items=cart_items,
                cart_found=cart_found,
                saved_found=saved_found,
                cart_total_price=cart_total_price,
                inventory_alert=False,
                balance_alert=False,
                coupon_alert=True,
                flag=0,
                discount=0)

def checkout(user_id,code): 
    user = User.get_by_uid(user_id)    
    pattern = r'^(\d+)coupon([0-4]?[0-9]|50)percentoff$'
    #valid coupon code
    if re.match(pattern, code):
        match=re.match(pattern, code)
        code_user_id = int(match.group(1))  
        discount = int(match.group(2)) 
    else:
        discount = 0
    
    cart_items = Cart.get(current_user.id)  
    cart_found  = any(not cart.c_status for cart in cart_items)
    saved_found = any( cart.c_status for cart in cart_items)
    cart_total_price=0
    flag=1
    for cart in cart_items:
        if cart.c_status==False:
            cart_total_price += (cart.total_price  * (Decimal('1.0') -  Decimal(0.01) * Decimal(discount))).quantize(Decimal('0.01'), rounding=ROUND_UP)
            if cart.c_quantity>Cart.get_stock(cart.c_pid,cart.c_sid):
                flag=0
    #check balance
    if user.balance>=cart_total_price:
        #check inventories
        if flag==1:
            Order.add_order(user.id)
            for cart in cart_items:
                if cart.c_status==False:
                    Order.add_items_to_order(cart.c_sid,cart.c_pid,(cart.c_price* (Decimal('1.0') -  Decimal(0.01) * Decimal(discount))).quantize(Decimal('0.01'), rounding=ROUND_UP),cart.c_quantity)
                    #update inventories and total sale
                    Product.update_stock_by_order(cart.c_pid,cart.c_sid,cart.c_quantity)
                    Product.update_total_sale(cart.c_pid,cart.c_sid,cart.c_quantity)
                    #update seller's balance
                    User.increase_balance(cart.c_sid,(cart.total_price * (Decimal('1.0') -  Decimal(0.01) * Decimal(discount))).quantize(Decimal('0.01'), rounding=ROUND_UP))
            orderKey=Order.find_max_order_key()
            orders= Order.get_by_oid_uid(user_id,orderKey)
            if orders is None or not orders:
                orders = []
           
            #update buyer's balance
            User.decrease_balance(user_id,(cart.total_price * (Decimal('1.0') -  Decimal(0.01) * Decimal(discount))).quantize(Decimal('0.01'), rounding=ROUND_UP))

            Cart.checkout(user.id)
            cart_total_price=0
            return render_template("order_detail.html",user=user,orders=orders)
        else:
             return render_template(
                "carts.html",
                user=user,
                cart_items=cart_items,
                cart_found=cart_found,
                saved_found=saved_found,
                cart_total_price=cart_total_price,
                inventory_alert=True,
                balance_alert=False,
                coupon_alert=False,
                flag=0,
                discount=discount)
    else:
        return render_template(
            "carts.html",
            user=user,
            cart_items=cart_items,
            cart_found=cart_found,
            saved_found=saved_found,
            cart_total_price=cart_total_price,
            inventory_alert=False,
            balance_alert=True ,
            coupon_alert=False,
            flag=0,
            discount=discount)

#seller part
@bp.route('/edit_products')
def edit_products():
    if not current_user.is_authenticated or not current_user.isSeller:
        # flash('You must be logged in as a seller to access this page.')
        return redirect(url_for('users.login'))

    products = Product.get_products_by_seller_id(current_user.id)  # get products that the seller is selling
    products_not_in_sell = Product.get_products_by_seller_id_not_in_sell(current_user.id) # get products that the seller does not sell
    categories = Product.get_unique_categories()
    return render_template('edit_products.html', products=products, products_not_in_sell=products_not_in_sell, categories=categories)
