from flask import current_app as app
from .product import Product
from datetime import datetime

class Cart:
    def __init__(self, id, pid, sid,price,quantity,s_firstname,s_lastname,status,productName,productDescription,image):
        self.c_uid = id
        self.c_pid = pid
        self.c_sid = sid
        self.c_price = price
        self.c_quantity = quantity
        self.s_firstname=s_firstname
        self.s_lastname=s_lastname
        self.c_status=status
        self.productName = productName
        self.productDescription = productDescription
        self.image=image
        self.total_price = price*quantity
        
    
    @staticmethod
    def get(uid):
        rows = app.db.execute('''
            SELECT c_uid, c_pid, c_sid, productseller.ps_price, c_quantity,users.u_firstname,users.u_lastname, c_status,products.p_productname,productseller.ps_description,productseller.ps_image
            FROM carts 
            JOIN users on carts.c_sid=users.u_uid
            JOIN products ON carts.c_pid = products.p_pid
            JOIN productseller on products.p_pid=productseller.ps_pid AND users.u_uid=productseller.ps_sid
            WHERE carts.c_uid = :uid
            ''', uid=uid)
        return [Cart(*row) for row in rows]
    
    @staticmethod
    def delete_item(uid, pid, sid):
        app.db.execute('''
            DELETE FROM carts
            WHERE c_uid=:uid 
            AND c_pid=:pid    
            AND c_sid=:sid
            ''', 
            uid = uid,
            pid = pid,
            sid = sid)
    
    @staticmethod
    def save_for_later(uid, pid, sid):
        app.db.execute('''
            UPDATE carts
            SET c_status=true
            WHERE c_uid=:uid 
            AND c_pid=:pid 
            AND c_sid=:sid
            ''', 
            uid = uid,
            pid = pid,
            sid = sid)
    
    @staticmethod
    def move_to_cart(uid, pid, sid):
        app.db.execute('''
            UPDATE carts
            SET c_status=false
            WHERE c_uid=:uid 
            AND c_pid=:pid 
            AND c_sid=:sid
            ''', 
            uid = uid,
            pid = pid,
            sid = sid)
    
    @staticmethod
    def change_quantity(uid, pid, sid, quantity):
        app.db.execute('''
            UPDATE carts
            SET c_quantity = :quantity
            WHERE c_uid = :uid
            AND c_pid = :pid
            AND c_sid = :sid
            ''', 
            uid = uid,
            pid = pid,
            sid = sid,
            quantity = quantity)
    
    @staticmethod
    def checkout(uid):
        app.db.execute('''
            DELETE FROM carts
            WHERE c_uid=:uid 
            AND c_status=false 
            ''', 
            uid = uid)
    
    @staticmethod
    def add_to_cart(uid, pid, sid, quantity):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = app.db.execute('''
            UPDATE carts
            SET c_quantity = c_quantity + :quantity, c_date = :current_time, c_status = :c_status
            WHERE c_uid = :uid AND c_pid = :pid AND c_sid = :sid
            ''',
            uid=uid,
            pid=pid,
            sid=sid,
            current_time=current_time,
            c_status=False,
            quantity=quantity)
        if not result:
            app.db.execute('''
                INSERT INTO carts (c_uid, c_pid, c_sid, c_date, c_status, c_quantity)
                VALUES (:uid, :pid, :sid, :current_time, :c_status, :quantity)
                ''', 
                uid=uid,
                pid=pid,
                sid=sid,
                current_time=current_time,
                c_status=False,
                quantity=quantity)
        
    @staticmethod
    def get_stock(pid, sid): 
        result = app.db.execute('''
            SELECT ps_stock
            FROM productseller
            WHERE ps_pid=:pid 
            AND ps_sid=:sid 
            ''', 
            pid = pid,
            sid = sid)
        stock = result[0]
        return int(stock[0])