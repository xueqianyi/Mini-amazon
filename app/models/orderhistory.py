# A seller can browse/search the history of orders fulfilled or to be fulfilled
# sorted by in reverse chronological order by default. 
# For each order in this list
# show a summary 
# (buyer information including address, date order placed, total amount/number of items, and overall fulfillment status)

from flask import current_app as app

class Orderhistory:
    def __init__(self, orderkey, productname, pid, amount, number, date,  user_id, u_address, fulfilment, image):
        self.orderkey = orderkey
        self.productname = productname
        self.pid = pid
        self.date = date
        self.user_id = user_id
        self.fulfilment = fulfilment
        self.address = u_address
        self.amount = amount
        self.number = number
        self.image = image
    
    @staticmethod
    def get(id):   
        rows = app.db.execute('''
            select li_orderkey, p_productname, li_pid, li_amount, li_number, o_date, o_uid, u_address, li_fulfilment, ps_image
            from lineitems i
            inner join orders o on li_orderkey = o_orderkey
            inner join users u on u.u_uid = o.o_uid
            inner join productseller on productseller.ps_pid = i.li_pid and productseller.ps_sid = i.li_sid
            inner join products on products.p_pid = i.li_pid
            where li_sid = :sid
            order by o_date DESC
            ''', sid=id)
        return [Orderhistory(*row) for row in rows]

    @staticmethod
    def update_fulfilment(orderkey, pid, sid, new_status):
        res = app.db.execute('''
            UPDATE lineitems
            SET li_fulfilment=:new_status
            WHERE li_orderkey=:orderkey
            AND li_sid=:sid
            AND li_pid=:pid
            ''', 
            orderkey=orderkey,
            pid=pid,
            sid=sid,
            new_status=new_status)
        print(res)