from flask import current_app as app
from datetime import datetime
class Order:
    def __init__(self, order_key, date, uid, pid, category, product_name, sid, number, amount,img,description,status,ship_date,deliver_date):
        self.order_key = order_key
        self.date = date  ## processing date
        self.uid = uid
        self.pid = pid
        self.category = category
        self.product_name = product_name
        self.sid = sid
        self.number = number
        self.amount = amount
        self.img = img
        self.description = description
        self.status = status
        self.ship_date=ship_date
        self.deliver_date=deliver_date

    

    @staticmethod
    def get_by_oid_uid(uid,oid):
        rows = app.db.execute('''
            SELECT o.o_orderKey, o.o_date, li.li_pid, li.li_sid, li.li_amount, li.li_number, p.p_category, p.p_productName, ps.ps_image, ps.ps_description, li.li_fulfilment,li.li_ship_date,li.li_deliver_date
            FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            JOIN products AS p ON p.p_pid = li.li_pid
            JOIN productSeller AS ps ON ps.ps_pid = li.li_pid AND ps.ps_sid = li.li_sid
            WHERE o.o_uid = :uid AND o.o_orderKey = :oid
            ORDER BY o.o_date DESC
        ''', uid=uid,oid=oid)
        return [Order(order_key=row[0], date=row[1], uid=uid, pid=row[2], sid=row[3], 
                      amount=row[4], number=row[5], category=row[6], 
                      product_name=row[7],img = row[8],description = row[9],status=row[10],ship_date=row[11],deliver_date=row[12]) for row in rows]
       
    @staticmethod
    def get_by_uid(uid):
        print("---------order query------------------")
        rows = app.db.execute('''
            SELECT o.o_orderKey, o.o_date, li.li_pid, li.li_sid, li.li_amount, li.li_number, p.p_category, p.p_productName,ps.ps_image, ps.ps_description, li.li_fulfilment,li.li_ship_date,li.li_deliver_date
            FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            JOIN products AS p ON p.p_pid = li.li_pid
            JOIN productSeller AS ps ON ps.ps_pid = li.li_pid AND ps.ps_sid = li.li_sid
            WHERE o.o_uid = :uid
            ORDER BY o.o_date DESC
        ''', uid=uid)
       
        return [Order(order_key=row[0], date=row[1], uid=uid, pid=row[2], sid=row[3], 
                      amount=row[4], number=row[5], category=row[6], 
                      product_name=row[7],img = row[8],description = row[9],status=row[10],ship_date=row[11],deliver_date=row[12]) for row in rows]


    @staticmethod
    def get_total_orders_count(uid):
         result = app.db.execute('''
SELECT COUNT(*) FROM orders
WHERE o_uid = :uid
''', uid=uid)
         return result[0][0] if result else 0
    
    @staticmethod
    def add_order(uid):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orderKey = app.db.execute('''
            SELECT MAX(o_orderkey)
            FROM orders
        ''')[0][0]
        new_orderkey=orderKey+1
        app.db.execute('''
            INSERT INTO orders(o_orderkey,o_date,o_uid)
            VALUES (:new_orderkey,:current_time, :uid)
            ''', 
            new_orderkey=new_orderkey,
            current_time=current_time,
            uid=uid)
            
    @staticmethod
    def have_bought_seller(uid, sid):
        result = app.db.execute('''
            SELECT COUNT(*) FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            WHERE o.o_uid = :uid AND li.li_sid = :sid
        ''', uid=uid, sid=sid)
        return result[0][0] if result else 0
    
    @staticmethod
    def have_bought_product(uid, pid, sid):
        result = app.db.execute('''
            SELECT COUNT(*) FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            WHERE o.o_uid = :uid AND li.li_pid = :pid AND li.li_sid = :sid
        ''', uid=uid, pid=pid, sid=sid)
        return result[0][0] if result else 0


    @staticmethod
    def add_items_to_order(sid,pid,amount,number):
        orderKey = app.db.execute('''
            SELECT MAX(o_orderkey)
            FROM orders
        ''')[0][0]

        app.db.execute('''
            INSERT INTO lineitems(li_orderKey,li_sid,li_pid,li_amount,li_number,li_fulfilment)
            VALUES (:orderKey,:sid,:pid,:amount,:number,:fulfilment)
                ''', 
                orderKey=orderKey,
                sid=sid,
                pid=pid,
                amount=amount,
                number=number,
                fulfilment='Processing')
    
     
    @staticmethod
    def find_max_order_key():   
        orderKey = app.db.execute('''
            SELECT MAX(o_orderkey)
            FROM orders
        ''')[0][0]
        return orderKey
    

    @staticmethod
    def get_order_status(uid,oid):
        orders=app.db.execute('''
            SELECT o.o_orderKey, o.o_date, o.o_uid,li.li_pid, p.p_category, p.p_productName,li.li_sid, li.li_number,  
                li.li_amount, ps.ps_image, ps.ps_description, li.li_fulfilment,li.li_ship_date,li.li_deliver_date
            FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            JOIN products AS p ON p.p_pid = li.li_pid
            JOIN productSeller AS ps ON ps.ps_pid = li.li_pid AND ps.ps_sid = li.li_sid
            WHERE o.o_uid = :uid AND o.o_orderKey = :oid
            ORDER BY o.o_date DESC
        ''', uid=uid,oid=oid)
        statuses = [order[11] for order in orders]
        if 'Processing' in statuses:
            overall_status = 'Processing'
        elif 'Shipped' in statuses:
            overall_status = 'Shipped'
        elif all(status == 'Delivered' for status in statuses):
            overall_status = 'Delivered'
        else:
            overall_status = 'Unknown'
        return overall_status
    
    @staticmethod
    def get_order_status_date(uid, oid):
        orders = app.db.execute('''
            SELECT o.o_orderKey, o.o_date, o.o_uid,li.li_pid, p.p_category, p.p_productName,li.li_sid, li.li_number, 
                li.li_amount, ps.ps_image, ps.ps_description, li.li_fulfilment,li.li_ship_date,li.li_deliver_date
            FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            JOIN products AS p ON p.p_pid = li.li_pid
            JOIN productSeller AS ps ON ps.ps_pid = li.li_pid AND ps.ps_sid = li.li_sid
            WHERE o.o_uid = :uid AND o.o_orderKey = :oid
            ORDER BY o.o_date DESC
        ''', uid=uid,oid=oid)

        if not orders:
            return None  

        statuses = [order[11] for order in orders]
        date = None

        if 'Processing' in statuses:
            overall_status = 'Processing'
            date = min(order[1] for order in orders if order[11] == 'Processing')

        elif 'Shipped' in statuses:
            overall_status = 'Shipped'
            date = min(order[12] for order in orders if order[11] == 'Shipped')

        elif all(status == 'Delivered' for status in statuses):
            overall_status = 'Delivered'
            date = min(order[13] for order in orders)

        else:
            overall_status = 'Unknown'
            date = datetime.now()

        return date

    @staticmethod
    def get_order_final_price(uid,oid):
        orders=app.db.execute('''
            SELECT o.o_orderKey, o.o_date, li.li_pid, li.li_sid, li.li_amount, li.li_number, p.p_category, p.p_productName,ps.ps_image, ps.ps_description, li.li_fulfilment
            FROM orders AS o
            JOIN lineItems AS li ON li.li_orderKey = o.o_orderKey
            JOIN products AS p ON p.p_pid = li.li_pid
            JOIN productSeller AS ps ON ps.ps_pid = li.li_pid AND ps.ps_sid = li.li_sid
            WHERE o.o_uid = :uid AND o.o_orderKey = :oid
            ORDER BY o.o_date DESC
        ''', uid=uid,oid=oid)
        final_price=0
        for order in orders:
            final_price += order[4]*order[5]
        return final_price