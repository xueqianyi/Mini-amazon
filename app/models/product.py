from flask import current_app as app

class Product:    
    def __init__(self, sid, pid, name, category, stock, price, description, image, avgReviewRating, totalSale):
        self.sid = sid
        self.pid = pid
        self.name = name
        self.category = category
        self.stock = stock
        self.price = price
        self.description = description
        self.image = image
        self.avgReviewRating = avgReviewRating
        self.totalSale = totalSale

     
    @staticmethod
    def get_all():
        rows = app.db.execute('''
            SELECT ps.ps_sid, p_pid, p.p_productname,p.p_category,ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image,  ps.ps_avgreviewrating, ps.ps_totalsale
            FROM products p
            JOIN productSeller ps ON p.p_pid = ps.ps_pid
            ''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get(id):   
        rows = app.db.execute('''
            SELECT ps.ps_sid, p_pid, p.p_productname,p.p_category,ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image,  ps.ps_avgreviewrating, ps.ps_totalsale
            FROM products p
            JOIN productSeller ps ON p.p_pid = ps.ps_pid
            WHERE p_pid = :id
            ''', id=id)
        return Product(*rows[0]) if rows else None
    
    @staticmethod
    def get_products_by_sid(sid):
        rows = app.db.execute('''
            SELECT ps.ps_sid, ps.ps_pid, p.p_productName, p.p_category, ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image, ps.ps_avgreviewrating, ps.ps_totalsale
            FROM Products AS p
            JOIN ProductSeller AS ps ON p.p_pid = ps.ps_pid
            WHERE ps.ps_sid = :sid
            ''', sid=sid)
        print(rows)
        return [Product(*row) for row in rows]

    @staticmethod
    def search_and_sort(k, s, category, quantity=None, sid=None, pid=None):
        query = '''
        SELECT ps.ps_sid, ps.ps_pid, p.p_productName, p.p_category, ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image, ps.ps_avgreviewrating, ps.ps_totalsale
        FROM products p
        JOIN productSeller ps ON p.p_pid = ps.ps_pid
        WHERE POSITION(LOWER(:k) in LOWER(p_productname)) > 0
        '''
        # if sid:
        #     query += ' AND ps.ps_sid <> :sid '
        
        # if pid:
        #     query += ' AND ps.ps_pid <> :pid '

        if category and category != 'All':
            query += ' AND LOWER(p.p_category::text) = LOWER(:category)'
        
        if s == 'price-des-rank':
            query += ' ORDER BY ps.ps_price DESC'
        elif s == 'price-asc-rank':
            query += ' ORDER BY ps.ps_price ASC'
        elif s == 'review-rank':
            query += ' ORDER BY ps.ps_avgreviewrating DESC'
        elif s == 'exact-aware-popularity-rank':
            query += ' ORDER BY ps.ps_totalsale DESC'

        if quantity:
            query += ' LIMIT :quantity'

        rows = app.db.execute(query, k=k, category=category, quantity=quantity, sid=sid, pid=pid)
        return [Product(*row) for row in rows]
    
    def get_similar_products(pid):   
        rows = app.db.execute('''
            SELECT ps.ps_sid, p_pid, p.p_productname,p.p_category,ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image,  ps.ps_avgreviewrating, ps.ps_totalsale
            FROM products p
            JOIN productSeller ps ON p.p_pid = ps.ps_pid
            WHERE p_pid = :pid
            LIMIT 4
            ''', pid=pid)
        return [Product(*row) for row in rows]
        
    @staticmethod
    def get_product_by_sid_pid(sid, pid):
        rows = app.db.execute('''
            SELECT ps.ps_sid, ps.ps_pid, p.p_productName, p.p_category, ps.ps_stock, ps.ps_price, ps.ps_description, ps.ps_image, ps.ps_avgReviewRating, ps.ps_totalSale
            FROM Products AS p JOIN ProductSeller AS ps ON p.p_pid = ps.ps_pid
            WHERE ps.ps_sid = :sid AND ps.ps_pid = :pid
            ''', sid=sid, pid=pid)
        return Product(*rows[0]) if rows else None
    
    @staticmethod
    def get_products_by_seller_id(seller_id):
        rows = app.db.execute('''
            SELECT  ps.ps_sid,p.p_pid, p.p_productname,p.p_category,  ps.ps_stock,ps.ps_price, ps.ps_description, ps.ps_image,  ps.ps_avgreviewrating, ps.ps_totalsale
            FROM Products AS p
            JOIN ProductSeller AS ps ON p.p_pid = ps.ps_pid
            WHERE ps.ps_sid = :id
            ''', id=seller_id)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def update_stock(product_id, new_stock, seller_id):
        result = app.db.execute('''
            UPDATE ProductSeller
            SET ps_stock = :new_stock
            WHERE ps_pid = :product_id AND ps_sid = :seller_id
            ''', new_stock=new_stock,
                 product_id=product_id,
                 seller_id=seller_id)
        return result

    @staticmethod
    def update_description(product_id, new_description, seller_id):
        result = app.db.execute('''
            UPDATE ProductSeller
            SET ps_description = :new_description
            WHERE ps_pid = :product_id AND ps_sid = :seller_id
            ''', new_description=new_description,
                 product_id=product_id,
                 seller_id=seller_id)
        return result

    @staticmethod
    def update_price(product_id, new_price, seller_id):
        result = app.db.execute('''
            UPDATE ProductSeller
            SET ps_price = :new_price
            WHERE ps_pid = :product_id AND ps_sid = :seller_id
            ''', new_price=new_price,
                 product_id=product_id,
                 seller_id=seller_id)
        return result

    def update_image(product_id, new_image, seller_id):
        sql = """
        UPDATE ProductSeller
        SET ps_image = :new_image
        WHERE ps_pid = :product_id AND ps_sid = :seller_id
        """
        app.db.execute(sql, new_image=new_image, product_id=product_id, seller_id=seller_id)       
   
    @staticmethod
    def update_stock_by_order(product_id,seller_id,change):
        app.db.execute('''
            UPDATE ProductSeller
            SET ps_stock  = ps_stock - :change
            WHERE ps_pid = :product_id AND ps_sid = :seller_id
            ''', change=change,
                 product_id=product_id,
                 seller_id=seller_id)
    
    @staticmethod
    def update_total_sale(product_id,seller_id,change):
        app.db.execute('''
            UPDATE ProductSeller
            SET ps_totalsale  = ps_totalsale + :change
            WHERE ps_pid = :product_id AND ps_sid = :seller_id
            ''', change=change,
                 product_id=product_id,
                 seller_id=seller_id)
   
    @staticmethod
    def remove_product(product_id, seller_id):
        result = app.db.execute('''
            DELETE FROM ProductSeller
            WHERE ps_pid = :product_id AND ps_sid = :seller_id 
            ''', product_id=product_id,
                 seller_id=seller_id)
        print(result)
        return result
    
    @staticmethod
    def get_products_by_seller_id_not_in_sell(seller_id):
        rows = app.db.execute('''
            SELECT * FROM Products AS p
            WHERE p.p_pid NOT IN (SELECT p.p_pid
            FROM Products AS p
            JOIN ProductSeller AS ps ON p.p_pid = ps.ps_pid
            WHERE ps.ps_sid = :id) 
            ''', id=seller_id)
        return rows
    
    @staticmethod
    def insert_productseller_to_current_productseller(seller_id, product_id, price, stock):
        sql = """
        INSERT INTO ProductSeller
            (ps_sid, ps_pid, ps_price, ps_stock)
        values
            (:seller_id, :product_id, :price, :stock) """
        result = app.db.execute(sql, seller_id=seller_id, product_id=product_id, price=price, stock=stock)
        print(result)
        return result
    
    @staticmethod
    def update_avg_review_rating(sid, pid):
        rows = app.db.execute('''
        SELECT AVG(fp_score)
        FROM FeedbackProduct
        WHERE fp_pid = :pid AND fp_sid = :sid
        ''', pid=pid, sid=sid)

        avgReviewRating = rows[0][0] if rows[0][0] else 0
                
        app.db.execute('''
            UPDATE ProductSeller
            SET ps_avgReviewRating = :avgReviewRating
            WHERE ps_pid = :pid AND ps_sid = :sid
        ''', avgReviewRating=avgReviewRating, pid=pid, sid=sid)

    @staticmethod
    def get_unique_categories():
        rows = app.db.execute('''
            SELECT DISTINCT p.p_category
            FROM products p
        ''')
        return [row[0] for row in rows]

    @staticmethod
    def insert_new_product(category, name):
        sql = """
        INSERT INTO Products
            (p_category, p_productname)
        values
            (:category, :name) """
        result = app.db.execute(sql, category=category, name=name)
        print(result)
        return result